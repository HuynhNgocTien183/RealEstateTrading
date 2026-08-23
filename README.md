
---

## Yêu cầu hệ thống

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Git

---

## Hướng dẫn cài đặt

### 1. Cài đặt Backend (Django REST)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

Tạo file `.env` trong thư mục `backend/` với nội dung:
```env
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=realestate_db
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
```

Chạy migration và khởi động server:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Backend chạy tại: `http://127.0.0.1:8000/`

### 2. Cài đặt Frontend (Svelte)

```bash
cd frontend
npm install
npm run dev

pip install -r requirements.txt
```
Frontend chạy tại: `http://localhost:5173/`

### 3. Cài đặt môi trường AI/ML

```bash
cd ml
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

Mở và chạy `ml/notebooks/train_model.ipynb` để huấn luyện model. Model sau khi train sẽ được lưu vào `ml/models/best_model.pkl`, backend (`apps/predictions/`) sẽ load model này để dùng cho API dự đoán giá.

---

## Tính năng chính

### Người dùng
- Đăng ký / Đăng nhập (JWT Authentication, tự động refresh token)
- Đăng ký kèm chọn vai trò: Người mua hoặc Người bán
- Đăng ký / cập nhật hồ sơ kèm avatar
- Phân quyền: Người mua / Người bán / Admin

### Người bán
- Đăng tin bất động sản (thông tin, nhiều hình ảnh, vị trí, Google Maps)
- Quản lý danh sách tin đã đăng (Tin của tôi): xem trạng thái, sửa, xoá
- Sửa tin: cập nhật thông tin, thêm/xoá ảnh riêng biệt
- Xem lý do bị từ chối nếu tin không được duyệt

### Người mua
- Tìm kiếm, lọc bất động sản theo từ khoá, loại hình, quận/huyện, khoảng giá
- Xem chi tiết tin đăng: hình ảnh, thông số, bản đồ vị trí, lượt thích
- Lưu / bỏ tin yêu thích
- Xem tất cả tin đăng của 1 người bán
- Liên hệ người bán qua số điện thoại, Zalo, hoặc Email

### Admin
- Duyệt hoặc từ chối tin đăng, kèm lý do từ chối
- Xem danh sách tin theo 2 tab: Đang chờ duyệt / Đã từ chối
- Duyệt lại tin đã từng bị từ chối

### AI Dự đoán giá
- Nhập thông tin BĐS (diện tích, mặt tiền, đường vào, số tầng, số phòng, tình trạng pháp lý, nội thất, quận/huyện) - trả về giá dự đoán tham khảo
- Tích hợp trực tiếp ở trang chủ (dạng thu gọn) và trang chi tiết tin đăng
- Model tự động chọn thuật toán tốt nhất trong số Random Forest, Gradient Boosting, XGBoost, LightGBM, CatBoost dựa trên kết quả Cross-Validation

---

## API Endpoints

| STT | Phân hệ | Method | Endpoint | Quyền truy cập | Mô tả chi tiết |
| --- | --- | --- | --- | --- | --- |
| 1 | Authentication | POST | `/api/token/` | Public | Đăng nhập, lấy access + refresh token |
| 2 | Authentication | POST | `/api/token/refresh/` | Public | Làm mới access token bằng refresh token |
| 3 | Users | POST | `/api/users/register/` | Public | Đăng ký tài khoản mới (kèm avatar, vai trò), trả về JWT |
| 4 | Users | GET | `/api/users/me/` | Đã đăng nhập | Xem thông tin tài khoản hiện tại |
| 5 | Users | PATCH | `/api/users/me/` | Đã đăng nhập | Cập nhật hồ sơ (họ tên, email, SĐT, avatar) |
| 6 | Users | POST | `/api/users/logout/` | Đã đăng nhập | Đăng xuất (blacklist refresh token) |
| 7 | Listings | GET | `/api/listings/` | Public (theo phạm vi) | Danh sách tin — khách/mọi user chỉ thấy tin đã duyệt & đang bán; hỗ trợ lọc theo `property_type`, `district`, `price_min`, `price_max`, `seller`, tìm kiếm theo `search` |
| 8 | Listings | POST | `/api/listings/` | Đã đăng nhập | Tạo tin đăng mới kèm ảnh (mặc định pending, chờ duyệt) |
| 9 | Listings | GET | `/api/listings/{id}/` | Public (theo phạm vi) | Xem chi tiết 1 tin đăng |
| 10 | Listings | PATCH | `/api/listings/{id}/` | Chủ tin hoặc admin | Cập nhật thông tin tin đăng |
| 11 | Listings | DELETE | `/api/listings/{id}/` | Chủ tin hoặc admin | Xoá tin đăng |
| 12 | Listings | POST | `/api/listings/{id}/upload_images/` | Chủ tin hoặc admin | Thêm ảnh mới vào tin đã có |
| 13 | Listings | DELETE | `/api/listings/{id}/images/{image_id}/` | Chủ tin hoặc admin | Xoá 1 ảnh cụ thể khỏi tin |
| 14 | Listings | GET | `/api/listings/my_listings/` | Đã đăng nhập | Seller xem toàn bộ tin của chính mình (mọi trạng thái) |
| 15 | Listings | GET | `/api/listings/pending/` | Admin | Danh sách tin đang chờ duyệt |
| 16 | Listings | GET | `/api/listings/rejected/` | Admin | Danh sách tin đã bị từ chối |
| 17 | Listings | POST | `/api/listings/{id}/approve/` | Admin | Duyệt tin đăng |
| 18 | Listings | POST | `/api/listings/{id}/reject/` | Admin | Từ chối tin đăng (kèm lý do) |
| 19 | Predictions | POST | `/api/predictions/predict/` | Public | Nhập thông tin BĐS, nhận giá dự đoán từ AI |
| 20 | Predictions | GET | `/api/predictions/history/` | Đã đăng nhập | Xem lịch sử các lần đã dự đoán của mình |
| 21 | Interactions | GET | `/api/interactions/favorites/` | Đã đăng nhập | Danh sách tin yêu thích của mình |
| 22 | Interactions | POST | `/api/interactions/favorites/` | Đã đăng nhập | Thêm 1 tin vào yêu thích |
| 23 | Interactions | DELETE | `/api/interactions/favorites/{id}/` | Đã đăng nhập | Bỏ yêu thích |
| 24 | Django Admin | URL | `/admin/` | Admin | Trang quản trị |

---

## Ghi chú

Tính năng nhắn tin (messages) giữa người mua và người bán ban đầu có trong thiết kế nhưng đã không được thực hiện. Để gần với thực tiễn và đạt hiệu quả cao hơn, việc liên hệ được thực hiện qua số điện thoại, Zalo và Email hiển thị trực tiếp ở trang chi tiết tin đăng.

Hết.