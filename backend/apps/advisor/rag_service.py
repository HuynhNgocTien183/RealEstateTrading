import json
import logging
import os
import threading
from pathlib import Path

from django.conf import settings
from django.db.models import Count, Max, Prefetch

from apps.listings.models import Listing, ListingImage
from .knowledge import KNOWLEDGE_DOCS, KNOWLEDGE_VERSION

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_vectorstore = None
_loaded_fingerprint = None


PROMPT_TEMPLATE = """Bạn là chuyên gia tư vấn bất động sản của nền tảng RealEstateTrading (TP. Hồ Chí Minh).

Nhiệm vụ:
- Tư vấn dựa trên NGỮ CẢNH (tin đang bán trên sàn + kiến thức nền). Không bịa tin, giá, địa chỉ, số phòng.
- Chỉ giới thiệu những tin có trong ngữ cảnh. Nếu không có tin phù hợp, nói rõ và gợi ý nới ngân sách, đổi quận, hoặc dùng bộ lọc trang chủ.
- Trả lời tiếng Việt, rõ ràng, ưu tiên gạch đầu dòng khi liệt kê.
- Khi gợi ý tin: nêu tiêu đề, giá, diện tích, quận/huyện và mã tin (#ID).
- Phân biệt: AI dự đoán giá (form riêng, mô hình học máy) khác với bạn (chat tư vấn + gợi ý tin).
- Câu hỏi ngoài nhà đất / mua bán BĐS: lịch sự từ chối và kéo về tư vấn nhà đất.
- Không cam kết pháp lý hay khoản vay. Khuyên xem nhà thực tế và kiểm tra sổ trước khi đặt cọc.

Lịch sử hội thoại:
{history}

Ngữ cảnh truy xuất:
{context}

Câu hỏi của khách:
{question}
"""


def mark_index_stale():
    global _vectorstore, _loaded_fingerprint
    with _lock:
        _vectorstore = None
        _loaded_fingerprint = None
        meta_path = _index_dir() / 'index_meta.json'
        if meta_path.exists():
            try:
                meta_path.unlink()
            except OSError:
                pass


def _index_dir() -> Path:
    path = Path(getattr(settings, 'ADVISOR_INDEX_DIR', settings.BASE_DIR / 'media' / 'advisor_index'))
    path.mkdir(parents=True, exist_ok=True)
    return path


def _first_nonempty(*values):
    for value in values:
        if value and str(value).strip():
            return str(value).strip()
    return ''


def _get_api_key():
    key = _first_nonempty(
        getattr(settings, 'GOOGLE_API_KEY', ''),
        os.environ.get('GOOGLE_API_KEY', ''),
        os.environ.get('GEMINI_API_KEY', ''),
    )
    if not key:
        raise RuntimeError(
            'Chưa cấu hình GOOGLE_API_KEY. Tạo key tại https://aistudio.google.com/apikey '
            'rồi thêm vào backend/.env'
        )
    os.environ['GOOGLE_API_KEY'] = key
    os.environ.setdefault('GEMINI_API_KEY', key)
    return key


def _format_price(price):
    try:
        value = float(price)
    except (TypeError, ValueError):
        return 'Thoả thuận'
    if value >= 1_000_000_000:
        return f'{value / 1_000_000_000:.2f} tỷ VNĐ'
    if value >= 1_000_000:
        return f'{value / 1_000_000:.0f} triệu VNĐ'
    return f'{value:,.0f} VNĐ'


def _property_type_label(code):
    return {
        'house': 'Nhà phố',
        'apartment': 'Chung cư',
        'land': 'Đất nền',
        'villa': 'Biệt thự',
    }.get(code, code or 'Không rõ')


def _listing_queryset():
    return (
        Listing.objects.filter(
            approval_status=Listing.ApprovalStatus.APPROVED,
            status=Listing.Status.AVAILABLE,
        )
        .select_related('seller')
        .prefetch_related(
            Prefetch('images', queryset=ListingImage.objects.order_by('-is_primary', 'uploaded_at'))
        )
    )


def _fingerprint():
    stats = _listing_queryset().aggregate(count=Count('id'), latest=Max('updated_at'))
    latest = stats['latest'].isoformat() if stats['latest'] else 'none'
    return f"{stats['count']}:{latest}:k{KNOWLEDGE_VERSION}"


def _listing_to_text(listing):
    predicted = ''
    if listing.predicted_price:
        predicted = f"Giá AI dự đoán (tham khảo): {_format_price(listing.predicted_price)}\n"
    description = (listing.description or '').strip()
    if len(description) > 800:
        description = description[:800] + '…'
    return (
        f"TIN ĐĂNG #{listing.id}\n"
        f"Tiêu đề: {listing.title}\n"
        f"Loại hình: {_property_type_label(listing.property_type)}\n"
        f"Giá rao: {_format_price(listing.price)}\n"
        f"{predicted}"
        f"Diện tích: {listing.area} m²\n"
        f"Số tầng: {listing.floors or 'không rõ'}\n"
        f"Phòng ngủ: {listing.bedrooms}\n"
        f"Phòng tắm: {listing.bathrooms}\n"
        f"Địa chỉ: {listing.address}\n"
        f"Quận/huyện: {listing.district}\n"
        f"Thành phố: {listing.city}\n"
        f"Mô tả: {description or 'Không có mô tả.'}\n"
        f"Mã tin để dẫn link: {listing.id}\n"
    )


def _build_documents():
    from langchain_core.documents import Document

    docs = []
    for item in KNOWLEDGE_DOCS:
        docs.append(Document(
            page_content=f"KIẾN THỨC: {item['title']}\n{item['content'].strip()}",
            metadata={'doc_type': 'knowledge', 'source_id': item['id'], 'title': item['title']},
        ))

    for listing in _listing_queryset():
        docs.append(Document(
            page_content=_listing_to_text(listing),
            metadata={
                'doc_type': 'listing',
                'listing_id': listing.id,
                'title': listing.title,
                'district': listing.district,
                'city': listing.city,
                'property_type': listing.property_type,
                'price': str(listing.price),
                'area': str(listing.area),
            },
        ))
    return docs


def _embeddings():
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    _get_api_key()
    model = getattr(settings, 'GEMINI_EMBEDDING_MODEL', 'models/gemini-embedding-001')
    return GoogleGenerativeAIEmbeddings(model=model)


def _load_meta():
    path = _index_dir() / 'index_meta.json'
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return None


def _save_meta(fingerprint, doc_count):
    path = _index_dir() / 'index_meta.json'
    path.write_text(
        json.dumps({'fingerprint': fingerprint, 'doc_count': doc_count}, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )


def rebuild_index():
    global _vectorstore, _loaded_fingerprint
    from langchain_community.vectorstores import FAISS

    _get_api_key()
    docs = _build_documents()
    if not docs:
        raise RuntimeError('Không có dữ liệu để lập chỉ mục tư vấn.')

    embeddings = _embeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)
    index_dir = _index_dir()
    vectorstore.save_local(str(index_dir))
    fingerprint = _fingerprint()
    _save_meta(fingerprint, len(docs))

    with _lock:
        _vectorstore = vectorstore
        _loaded_fingerprint = fingerprint
    logger.info('Rebuilt advisor FAISS index: %s docs, fingerprint=%s', len(docs), fingerprint)
    return {'doc_count': len(docs), 'fingerprint': fingerprint}


def _load_vectorstore():
    global _vectorstore, _loaded_fingerprint
    from langchain_community.vectorstores import FAISS

    fingerprint = _fingerprint()
    with _lock:
        if _vectorstore is not None and _loaded_fingerprint == fingerprint:
            return _vectorstore

    meta = _load_meta()
    index_faiss = _index_dir() / 'index.faiss'
    index_pkl = _index_dir() / 'index.pkl'
    if meta and meta.get('fingerprint') == fingerprint and index_faiss.exists() and index_pkl.exists():
        vectorstore = FAISS.load_local(
            str(_index_dir()),
            _embeddings(),
            allow_dangerous_deserialization=True,
        )
        with _lock:
            _vectorstore = vectorstore
            _loaded_fingerprint = fingerprint
        return vectorstore

    result = rebuild_index()
    return _vectorstore


def _format_history(history):
    if not history:
        return '(Không có)'
    lines = []
    for item in history[-6:]:
        role = 'Khách' if item.get('role') == 'user' else 'AI'
        content = (item.get('content') or '').strip()
        if content:
            lines.append(f'{role}: {content}')
    return '\n'.join(lines) if lines else '(Không có)'


def _retrieval_query(question, history):
    parts = [question]
    if history:
        for item in reversed(history):
            if item.get('role') == 'user' and (item.get('content') or '').strip():
                prev = item['content'].strip()
                if prev != question:
                    parts.insert(0, prev)
                break
    return '\n'.join(parts)


def listing_payload(listing, request=None):
    images = list(listing.images.all())
    image_url = None
    if images:
        image = images[0].image
        if image:
            image_url = image.url
            if request:
                image_url = request.build_absolute_uri(image_url)
    return {
        'id': listing.id,
        'title': listing.title,
        'price': str(listing.price),
        'area': str(listing.area),
        'bedrooms': listing.bedrooms,
        'bathrooms': listing.bathrooms,
        'district': listing.district,
        'city': listing.city,
        'address': listing.address,
        'property_type': listing.property_type,
        'image': image_url,
    }


def ask(question, history=None, request=None):
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI

    question = (question or '').strip()
    if not question:
        raise ValueError('Câu hỏi không được để trống.')

    _get_api_key()
    vectorstore = _load_vectorstore()
    k = int(getattr(settings, 'ADVISOR_RETRIEVE_K', 6))
    retriever = vectorstore.as_retriever(search_type='similarity', search_kwargs={'k': k})
    docs = retriever.invoke(_retrieval_query(question, history or []))

    context = '\n\n---\n\n'.join(doc.page_content for doc in docs) if docs else 'Không có ngữ cảnh.'
    llm = ChatGoogleGenerativeAI(
        model=getattr(settings, 'GEMINI_MODEL', 'gemini-3.6-flash'),
        temperature=0.3,
    )
    chain = ChatPromptTemplate.from_template(PROMPT_TEMPLATE) | llm | StrOutputParser()
    answer = chain.invoke({
        'context': context,
        'question': question,
        'history': _format_history(history),
    })

    listing_ids = []
    for doc in docs:
        listing_id = doc.metadata.get('listing_id')
        if listing_id and listing_id not in listing_ids:
            listing_ids.append(listing_id)

    sources = []
    if listing_ids:
        listings = {item.id: item for item in _listing_queryset().filter(id__in=listing_ids)}
        for listing_id in listing_ids:
            listing = listings.get(listing_id)
            if listing:
                sources.append(listing_payload(listing, request=request))

    return {
        'answer': answer.strip(),
        'sources': sources,
        'model': getattr(settings, 'GEMINI_MODEL', 'gemini-3.6-flash'),
    }
