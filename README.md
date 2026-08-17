# 🏠 RealEstateTrading

Nền tảng mua bán, đăng tin bất động sản trực tuyến, tích hợp **AI dự đoán giá nhà** giúp người bán định giá hợp lý và người mua tham khảo giá thị trường.

---

## 📌 Giới thiệu

**RealEstateTrading** là hệ thống web cho phép:
- **Người bán**: đăng tin bất động sản, quản lý tin đăng, tương tác với người mua (nhắn tin, phản hồi).
- **Người mua**: tìm kiếm, lọc bất động sản theo tiêu chí, xem chi tiết, liên hệ người bán.
- **AI Dự đoán giá**: dựa trên các đặc trưng (diện tích, vị trí, số phòng, loại hình BĐS...), hệ thống gợi ý mức giá hợp lý cho tin đăng, giúp minh bạch hoá thị trường và hỗ trợ ra quyết định.

---

## 🛠️ Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| **Backend** | Django, Django REST Framework (DRF) |
| **Frontend** | Svelte + Vite (JavaScript) |
| **Database** | MySQL |
| **AI / Machine Learning** | Python (scikit-learn / XGBoost), Pandas, Numpy |
| **Authentication** | JWT (Django REST Framework SimpleJWT) |
| **Khác** | Docker (tuỳ chọn), Git |

---

## 📁 Cấu trúc dự án

```
RealEstateTrading/
│
├── backend/                    # Django REST API
│   ├── manage.py
│   ├── config/                  # settings.py, urls.py, wsgi/asgi
│   ├── apps/
│   │   ├── users/                # đăng ký, đăng nhập, phân quyền (buyer/seller)
│   │   ├── listings/              # đăng tin, tìm kiếm, quản lý BĐS
│   │   ├── interactions/          # chat, yêu thích, đánh giá, liên hệ
│   │   └── predictions/           # tích hợp model AI, API dự đoán giá
│   ├── requirements.txt
│   └── .venv/
│
├── frontend/                    # Giao diện người dùng (Svelte)
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api.js             # gọi API backend
│   │   │   ├── components/        # ListingCard, PredictionForm, Navbar...
│   │   │   └── stores/            # quản lý state (auth, cart...)
│   │   ├── routes/                # các trang: Home, Listings, PostListing, Login...
│   │   ├── App.svelte
│   │   └── main.js
│   └── package.json
│
├── ml/                           # Huấn luyện & thử nghiệm mô hình AI
│   ├── notebooks/                 # EDA, thử nghiệm (Jupyter)
│   ├── data/
│   │   ├── raw/                    # dữ liệu gốc
│   │   └── processed/              # dữ liệu đã xử lý
│   ├── src/
│   │   ├── preprocess.py
│   │   ├── train.py
│   │   └── evaluate.py
│   ├── models/                     # model đã train (.pkl / .joblib)
│   ├── requirements.txt
│   └── .venv/
│
├── docs/                          # tài liệu dự án (báo cáo, sơ đồ, đặc tả)
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Yêu cầu hệ thống

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

Huấn luyện model:
```bash
python src/train.py
```
Model sau khi train sẽ được lưu vào `ml/models/`, backend (`apps/predictions/`) sẽ load model này để phục vụ API dự đoán giá.

---

## Tính năng chính

### Người dùng
- [ ] Đăng ký / Đăng nhập (JWT Authentication)
- [ ] Phân quyền: Người mua / Người bán / Admin

### Người bán
- [ ] Đăng tin bất động sản (thông tin, hình ảnh, vị trí)
- [ ] Quản lý danh sách tin đã đăng (sửa/xoá/ẩn)
- [ ] Xem gợi ý giá bán từ AI khi đăng tin
- [ ] Tương tác, phản hồi tin nhắn từ người mua

### Người mua
- [ ] Tìm kiếm, lọc bất động sản (giá, vị trí, diện tích, loại hình)
- [ ] Xem chi tiết tin đăng
- [ ] Lưu tin yêu thích
- [ ] Liên hệ / nhắn tin với người bán

### AI Dự đoán giá
- [ ] Nhập thông tin BĐS (diện tích, vị trí, số phòng...) → trả về khoảng giá dự đoán
- [ ] Hiển thị mức độ tin cậy của dự đoán
- [ ] So sánh giá đăng bán với giá AI đề xuất

---

## 📡 API Endpoints

| STT | Phân hệ (Module) | Method | Endpoint | Quyền truy cập | Mô tả chi tiết |
| --- | --- | --- | --- | --- | --- |
| 1 | **Authentication** | `POST` | `/api/token/` | Public | Đăng nhập, lấy access + refresh token |
| 2 | **Authentication** | `POST` | `/api/token/refresh/` | Public | Làm mới access token bằng refresh token |
| 3 | **App users** | `POST` | `/api/users/register/` | Public | Đăng ký tài khoản mới, trả về JWT |
| 4 | **App users** | `GET` | `/api/users/me/` | Đã đăng nhập | Xem thông tin tài khoản hiện tại |
| 5 | **App users** | `POST` | `/api/users/logout/` | Đã đăng nhập | Đăng xuất (blacklist refresh token) |
| 6 | **App listings** | `GET` | `/api/listings/` | Public (theo phạm vi) | Danh sách tin đăng — khách chỉ thấy bài đã duyệt & đang bán |
| 7 | **App listings** | `POST` | `/api/listings/` | Đã đăng nhập | Tạo tin đăng mới (mặc định pending, chờ duyệt) |
| 8 | **App listings** | `GET` | `/api/listings/{id}/` | Public (theo phạm vi) | Xem chi tiết 1 tin đăng |
| 9 | **App listings** | `PUT` / `PATCH` | `/api/listings/{id}/` | Chủ tin hoặc admin | Cập nhật tin đăng |
| 10 | **App listings** | `DELETE` | `/api/listings/{id}/` | Chủ tin hoặc admin | Xoá tin đăng |
| 11 | **App listings** | `GET` | `/api/listings/my_listings/` | Đã đăng nhập | Seller xem toàn bộ tin của chính mình (mọi trạng thái) |
| 12 | **App listings** | `GET` | `/api/listings/pending/` | Admin | Danh sách tin đang chờ duyệt |
| 13 | **App listings** | `POST` | `/api/listings/{id}/approve/` | Admin | Duyệt tin đăng |
| 14 | **App listings** | `POST` | `/api/listings/{id}/reject/` | Admin | Từ chối tin đăng (kèm reason) |
| 15 | **App predictions** | `POST` | `/api/predictions/predict/` | Public | Nhập thông tin BĐS, nhận giá dự đoán từ AI |
| 16 | **App predictions** | `GET` | `/api/predictions/history/` | Đã đăng nhập | Xem lịch sử các lần đã dự đoán của mình |
| 17 | **App interactions** | `GET` | `/api/interactions/favorites/` | Đã đăng nhập | Danh sách tin yêu thích của mình |
| 18 | **App interactions** | `POST` | `/api/interactions/favorites/` | Đã đăng nhập | Thêm 1 tin vào yêu thích |
| 19 | **App interactions** | `DELETE` | `/api/interactions/favorites/{id}/` | Đã đăng nhập | Bỏ yêu thích |
| 20 | **Django Admin** | `URL` | `/admin/` | Admin | Trang quản trị |


Hết.