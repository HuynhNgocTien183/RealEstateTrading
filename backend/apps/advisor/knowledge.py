KNOWLEDGE_VERSION = 2

KNOWLEDGE_DOCS = [
    {
        'id': 'platform-overview',
        'title': 'Giới thiệu RealEstateTrading',
        'content': """
RealEstateTrading là nền tảng mua bán nhà đất trực tuyến, tập trung nhà phố và bất động sản tại TP. Hồ Chí Minh.
Người mua có thể tìm tin, lọc theo quận, loại hình, khoảng giá, xem chi tiết, lưu yêu thích và liên hệ người bán qua điện thoại, Zalo hoặc email.
Người bán đăng tin (tiêu đề, mô tả, giá, diện tích, số tầng, phòng ngủ, phòng tắm, địa chỉ, ảnh, Google Maps). Tin mới phải chờ admin duyệt mới hiện trên trang chủ.
Hệ thống có AI dự đoán giá nhà phố TP.HCM (mô hình học máy v2) và AI tư vấn nhà đất (RAG + Gemini) để gợi ý tin đang bán trên sàn.
""",
    },
    {
        'id': 'how-to-search',
        'title': 'Cách tìm và lọc nhà đất',
        'content': """
Trên trang chủ, người dùng tìm theo từ khoá (tiêu đề, mô tả, địa chỉ), loại hình (nhà phố, chung cư, đất nền, biệt thự), quận/huyện và khoảng giá.
Nên nêu rõ ngân sách, quận, số phòng ngủ, diện tích khi hỏi AI để hệ thống gợi ý tin phù hợp hơn.
Xem chi tiết tin để thấy ảnh, thông số, mô tả, bản đồ và thông tin liên hệ người bán.
Nếu chưa đăng nhập vẫn xem tin được; lưu yêu thích và xem lịch sử định giá thì cần tài khoản.
""",
    },
    {
        'id': 'price-ai',
        'title': 'AI dự đoán giá nhà',
        'content': """
Form "Dùng AI dự đoán giá nhà" trên trang chủ và trang chi tiết tin dùng mô hình máy học (best_model_v2), học từ dữ liệu nhà phố TP.HCM năm 2024.
Đầu vào: diện tích (bắt buộc), mặt tiền, đường vào, số tầng, phòng ngủ, phòng tắm, pháp lý, nội thất, quận/huyện.
Kết quả là giá tham khảo bằng VNĐ, không phải giá giao dịch thật. Người bán dùng để định giá tin; người mua dùng để đối chiếu với giá rao.
Lịch sử định giá xem tại trang Lịch sử định giá khi đã đăng nhập.
AI tư vấn (chat) khác với AI dự đoán giá: chat dùng RAG để gợi ý tin đang bán và tư vấn nhu cầu; form dự đoán dùng mô hình hồi quy để ước giá.
""",
    },
    {
        'id': 'buy-tips-hcm',
        'title': 'Kinh nghiệm mua nhà TP.HCM',
        'content': """
Khi mua nhà tại TP.HCM nên xác định: ngân sách gồm giá nhà + phí sang tên + sửa chữa; nhu cầu ở hay đầu tư; khu vực làm việc, trường học, giao thông.
Nên xem nhà ban ngày, kiểm tra kết cấu, ngập nước, giấy tờ (sổ hồng/sổ đỏ), quy hoạch, ngõ vào, hướng nhà.
Nhà phố trung tâm (Quận 1, 3, 5, 10, Phú Nhuận) thường đắt hơn, tiện đi lại. Khu phía đông (Quận 2/Thủ Đức, Quận 9 cũ) và Nam (Quận 7, Nhà Bè) phù hợp nhà mới, diện tích lớn hơn cùng tầm giá.
Đừng chốt chỉ vì giá rẻ: so sánh giá/m² với các tin cùng quận trên sàn. Dùng AI dự đoán giá để có mốc tham khảo.
Luôn thương lượng, đặt cọc có hợp đồng, và nếu cần thì nhờ luật sư hoặc công chứng viên kiểm tra pháp lý.
""",
    },
    {
        'id': 'property-types',
        'title': 'Các loại hình bất động sản trên sàn',
        'content': """
Nhà phố (house): phổ biến nhất trên sàn, thường 2-5 tầng, phù hợp ở kết hợp kinh doanh nếu mặt tiền.
Chung cư (apartment): quản lý phí, tiện ích, phù hợp gia đình nhỏ, an ninh tốt hơn nhà mặt đất.
Đất nền (land): cần kiểm tra quy hoạch, hạ tầng, thời điểm xây được.
Biệt thự (villa): diện tích lớn, giá cao, thường ở khu compound hoặc đường lớn.
Khi hỏi AI, nêu loại hình mong muốn để lọc đúng tin.
""",
    },
    {
        'id': 'legal-basics',
        'title': 'Pháp lý nhà đất cơ bản',
        'content': """
Sổ hồng / sổ đỏ (Have certificate): tài sản đã có giấy chứng nhận, giao dịch thuận lợi hơn.
Hợp đồng mua bán (Sale contract): chưa ra sổ, rủi ro cao hơn, cần xem tiến độ sang tên.
Đang chờ sổ (Pending): hỏi rõ lý do và thời gian dự kiến.
Nên đối chiếu thông tin trên tin đăng với giấy tờ gốc, bản đồ quy hoạch, và xem nhà trực tiếp.
AI tư vấn không thay thế thẩm định pháp lý. Không đưa số tài khoản, CCCD hay đặt cọc qua chat.
""",
    },
    {
        'id': 'budget-guide',
        'title': 'Gợi ý ngân sách mua nhà',
        'content': """
Dưới 4 tỷ: thường là nhà nhỏ, hẻm, hoặc khu xa trung tâm (Quận 12, huyện ngoại thành, một số căn Quận 8/9).
Khoảng 4-7 tỷ: nhiều nhà phố 2-4 tầng, 2-4 phòng ngủ ở các quận trung bình (Gò Vấp, Tân Bình, Tân Phú, Bình Tân, một phần Quận 7).
Trên 7-10 tỷ: nhà rộng hơn, vị trí đẹp hơn, có thể mặt tiền hoặc khu đắc địa.
Trên 10 tỷ: biệt thự, nhà mặt tiền trung tâm, diện tích lớn.
Giá trên sàn là giá rao, có thể thương lượng. Nêu ngân sách khi hỏi AI để được gợi ý sát hơn.
""",
    },
    {
        'id': 'contact-seller',
        'title': 'Liên hệ người bán và lưu tin',
        'content': """
Trên trang chi tiết tin có số điện thoại, Zalo, email người bán (nếu họ đã khai).
Đăng nhập để lưu yêu thích, xem lại sau tại trang Yêu thích.
Không chuyển tiền trước khi xem nhà và ký giấy tờ. Nền tảng chỉ trung gian đăng tin, không giữ tiền hộ.
Nếu tin có Google Maps, dùng bản đồ để xem vị trí thực tế trước khi đi xem nhà.
""",
    },
]
