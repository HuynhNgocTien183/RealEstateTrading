from django.core.management.base import BaseCommand
from apps.advisor.rag_service import rebuild_index


class Command(BaseCommand):
    help = 'Lập lại chỉ mục FAISS cho AI tư vấn nhà đất từ tin đã duyệt và kiến thức nền.'

    def handle(self, *args, **options):
        try:
            result = rebuild_index()
        except Exception as exc:
            self.stderr.write(self.style.ERROR(str(exc)))
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS(
            f"Đã lập chỉ mục {result['doc_count']} tài liệu (fingerprint={result['fingerprint']})."
        ))
