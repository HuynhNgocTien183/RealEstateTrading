# RealEstateTrading

Nền tảng mua bán, đăng tin bất động sản trực tuyến, tích hợp AI dự đoán giá nhà phố TP.HCM để người bán định giá và người mua tham khảo giá thị trường.

---

## Giới thiệu

RealEstateTrading là hệ thống web gồm 3 vai trò:

- **Người bán:** đăng tin, quản lý tin (sửa / xoá / thêm-xoá ảnh), theo dõi trạng thái duyệt và lý do từ chối.
- **Người mua:** tìm kiếm, lọc tin, xem chi tiết, lưu yêu thích, xem tin của một người bán, liên hệ qua SĐT / Zalo / Email.
- **Admin:** duyệt hoặc từ chối tin, xem lại tin đã từ chối.

AI dự đoán giá dùng mô hình **v2** (`best_model_v2.pkl`), học trên dữ liệu nhà phố TP.HCM 2024. Có thể để trống tầng / phòng / mặt tiền / đường vào — hệ thống điền theo thống kê lúc train.

---

## Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Backend | Django 6, Django REST Framework, django-filter, django-cors-headers |
| Frontend | Svelte 5 + Vite, svelte-spa-router, Axios, @lucide/svelte |
| Database | MySQL 8 |
| Cache | Redis (tuỳ chọn, lỗi Redis không chặn API) |
| AI / ML | Python, Pandas, NumPy, scikit-learn, XGBoost, LightGBM, CatBoost, Jupyter |
| Authentication | JWT (`djangorestframework-simplejwt`), refresh + blacklist |
| Khác | Git, Pillow (ảnh avatar / tin đăng) |

---

## Cấu trúc dự án

```
RealEstateTrading/
│
├── backend/                          # Django REST API
│   ├── manage.py
│   ├── config/                       # settings, urls, wsgi/asgi
│   ├── apps/
│   │   ├── users/                    # đăng ký, JWT, hồ sơ, đổi mật khẩu, vai trò
│   │   ├── listings/                 # tin đăng, ảnh, tìm kiếm, duyệt tin
│   │   │   └── management/commands/
│   │   │       └── seed_listings.py  # tạo 30 tin mẫu từ CSV 2024
│   │   ├── interactions/             # tin yêu thích
│   │   └── predictions/              # ml_service.py + API dự đoán / lịch sử
│   ├── media/                        # avatar, ảnh tin đăng
│   ├── requirements.txt
│   └── .env                          # cấu hình DB, SECRET_KEY (không commit)
│
├── frontend/                         # Giao diện Svelte (hash router)
│   ├── public/                       # logo.png
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api/                  # auth, listings, interactions, predictions
│   │   │   ├── components/           # Navbar, ListingCard, SearchBar, PredictionForm
│   │   │   └── stores/               # auth, homeState
│   │   ├── pages/                    # Home, ListingDetail, CreateListing, MyListing,
│   │   │                            # AdminReview, Login, Register, Profile,
│   │   │                            # SavedListings, SellerListings, PredictionHistory
│   │   ├── styles/
│   │   ├── routes.js
│   │   ├── App.svelte
│   │   └── main.js
│   └── package.json
│
├── ml/
│   ├── notebooks/
│   │   ├── train.ipynb               # bản gốc → best_model.pkl (v1)
│   │   ├── train_v2.ipynb            # đang dùng trên API → best_model_v2.pkl
│   │   └── train_v3.ipynb            # thử nghiệm dữ liệu 2025 (chưa gắn API)
│   ├── data/raw/
│   │   ├── DuLieuGiaNhaHCM2024.csv
│   │   └── DuLieuGiaNhaHCM2025.csv
│   ├── models/                       # file .pkl sau khi train
│   └── requirements.txt
│
└── README.md
```

---

## Yêu cầu hệ thống

- Python 3.12+ (Django 6)
- Node.js 18+
- MySQL 8.0+
- Redis (tuỳ chọn, dùng cache danh sách / chi tiết tin)
- Git

---

## Hướng dẫn cài đặt

### 1. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

Tạo file `.env` trong `backend/`:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=realestate_db
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=3306
```

Tạo database MySQL (charset `utf8mb4`), rồi:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

Backend: `http://127.0.0.1:8000/`  
Admin Django: `http://127.0.0.1:8000/admin/`

Frontend gọi API tại `http://127.0.0.1:8000/api` (xem `frontend/src/lib/api/client.js`).

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173/`

### 3. Dữ liệu tin mẫu

Cần ít nhất một tài khoản `seller`. Sau đó:

```bash
cd backend
python manage.py seed_listings --clear
```

Lệnh lấy 30 căn nhà phố đủ số liệu từ `ml/data/raw/DuLieuGiaNhaHCM2024.csv`, gán ngẫu nhiên cho các seller, duyệt sẵn (`approved`). `--clear` xoá toàn bộ tin/ảnh cũ trước khi tạo.

### 4. Môi trường AI / ML

```bash
cd ml
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Chạy `ml/notebooks/train_v2.ipynb` để tạo `ml/models/best_model_v2.pkl`. Backend ưu tiên file này; nếu thiếu sẽ thử `best_model.pkl` (v1).

Phiên bản scikit-learn / XGBoost lúc train phải khớp `backend/requirements.txt` (`scikit-learn==1.8.0`, `xgboost==3.4.1`) để `joblib.load` không lỗi.

---

## Tính năng chính

### Tài khoản

- Đăng ký / đăng nhập JWT (access 1 giờ, refresh 7 ngày, tự refresh trên frontend)
- Chọn vai trò khi đăng ký: người mua hoặc người bán
- Hồ sơ: cập nhật tên đăng nhập, họ tên, email, SĐT, avatar
- Đổi mật khẩu
- Phân quyền buyer / seller / admin

### Người bán

- Đăng tin: tiêu đề, mô tả, giá, diện tích, tầng, phòng ngủ / tắm, loại hình, địa chỉ, quận, Google Maps, nhiều ảnh
- Tin mới ở trạng thái **chờ duyệt**
- **Tin của tôi:** xem trạng thái duyệt/bán, sửa, xoá, xem chi tiết (cùng tab)
- Sửa tin: cập nhật thông tin, thêm / xoá từng ảnh
- Xem lý do từ chối

### Người mua / khách

- Tìm theo từ khoá (tiêu đề, mô tả, địa chỉ), loại hình, quận/huyện, khoảng giá
- Xem chi tiết: ảnh, thông số, mô tả, bản đồ, lượt xem, lượt thích, người đăng
- Nút quay về (mũi tên) về trang trước
- Lưu / bỏ yêu thích (cần đăng nhập)
- Xem toàn bộ tin đã duyệt của một người bán
- Liên hệ: điện thoại, Zalo, email

### Admin

- Tab **Chờ duyệt** / **Đã từ chối**
- Duyệt hoặc từ chối (kèm lý do)
- Duyệt lại tin từng bị từ chối
- Xem chi tiết tin trên cùng tab

### AI dự đoán giá (model v2)

- Form trên trang chủ (thu gọn) và trang chi tiết tin
- Đầu vào: diện tích (bắt buộc), mặt tiền, đường vào, số tầng, phòng ngủ, phòng tắm, pháp lý, nội thất, quận/huyện
- Giá trả về đơn vị VNĐ; lịch sử lưu khi user đã đăng nhập
- Trang **Lịch sử định giá** xem các lần đã dự đoán
- Model so sánh Random Forest, Gradient Boosting, XGBoost, LightGBM, CatBoost trên tập 2024 (lọc nhà phố điển hình, `REL_MAX = 0.25`) rồi lưu mô hình tốt nhất

---

## API Endpoints

| STT | Phân hệ | Method | Endpoint | Quyền | Mô tả |
| --- | --- | --- | --- | --- | --- |
| 1 | Auth | POST | `/api/token/` | Public | Đăng nhập, lấy access + refresh |
| 2 | Auth | POST | `/api/token/refresh/` | Public | Làm mới access token |
| 3 | Users | POST | `/api/users/register/` | Public | Đăng ký (username, email, mật khẩu, vai trò, SĐT, avatar) |
| 4 | Users | GET | `/api/users/me/` | Đã đăng nhập | Thông tin tài khoản hiện tại |
| 5 | Users | PATCH | `/api/users/me/` | Đã đăng nhập | Cập nhật username, họ tên, email, SĐT, avatar |
| 6 | Users | POST | `/api/users/change-password/` | Đã đăng nhập | Đổi mật khẩu |
| 7 | Users | POST | `/api/users/logout/` | Đã đăng nhập | Đăng xuất (blacklist refresh token) |
| 8 | Listings | GET | `/api/listings/` | Public | Tin đã duyệt & đang bán. Lọc: `search`, `property_type`, `district`, `price_min`, `price_max`, `seller`, `bedrooms`, `status`. Sắp xếp: `ordering=price\|area\|created_at`. Phân trang 12 tin/trang |
| 9 | Listings | POST | `/api/listings/` | Seller | Tạo tin (mặc định pending) |
| 10 | Listings | GET | `/api/listings/{id}/` | Public (theo phạm vi) | Chi tiết tin, tăng `views_count` |
| 11 | Listings | PATCH | `/api/listings/{id}/` | Chủ tin hoặc admin | Cập nhật tin |
| 12 | Listings | DELETE | `/api/listings/{id}/` | Chủ tin hoặc admin | Xoá tin |
| 13 | Listings | POST | `/api/listings/{id}/upload_images/` | Chủ tin hoặc admin | Thêm ảnh |
| 14 | Listings | DELETE | `/api/listings/{id}/images/{image_id}/` | Chủ tin hoặc admin | Xoá một ảnh |
| 15 | Listings | GET | `/api/listings/my_listings/` | Đã đăng nhập | Toàn bộ tin của chính mình |
| 16 | Listings | GET | `/api/listings/pending/` | Admin | Tin chờ duyệt |
| 17 | Listings | GET | `/api/listings/rejected/` | Admin | Tin đã từ chối |
| 18 | Listings | POST | `/api/listings/{id}/approve/` | Admin | Duyệt tin |
| 19 | Listings | POST | `/api/listings/{id}/reject/` | Admin | Từ chối (kèm lý do) |
| 20 | Predictions | POST | `/api/predictions/predict/` | Public | Dự đoán giá; user đăng nhập thì lưu lịch sử |
| 21 | Predictions | GET | `/api/predictions/history/` | Đã đăng nhập | Lịch sử dự đoán của mình |
| 22 | Interactions | GET | `/api/interactions/favorites/` | Đã đăng nhập | Danh sách yêu thích |
| 23 | Interactions | POST | `/api/interactions/favorites/` | Đã đăng nhập | Thêm yêu thích |
| 24 | Interactions | DELETE | `/api/interactions/favorites/{id}/` | Đã đăng nhập | Bỏ yêu thích |
| 25 | Django Admin | — | `/admin/` | Staff / superuser | Trang quản trị |

---

## Route frontend

| Hash | Trang |
| --- | --- |
| `#/` | Trang chủ — tìm kiếm + danh sách tin + form AI |
| `#/login` | Đăng nhập |
| `#/register` | Đăng ký |
| `#/listings/:id` | Chi tiết tin |
| `#/create-listing` | Đăng tin (seller) |
| `#/edit-listing/:id` | Sửa tin |
| `#/my-listings` | Tin của tôi |
| `#/saved-listings` | Yêu thích |
| `#/seller/:id/listings` | Tin của một người bán |
| `#/prediction-history` | Lịch sử định giá |
| `#/profile` | Hồ sơ, avatar, đổi mật khẩu |
| `#/admin/review` | Duyệt tin (admin) |

---

## Ghi chú

- Không có chat trong hệ thống. Liên hệ qua SĐT, Zalo và email trên trang chi tiết tin.
- Redis không bắt buộc. Cache tin (TTL 15 phút) bỏ qua nếu Redis tắt.
- API dự đoán đang dùng **v2**. `train_v3.ipynb` (dữ liệu 2025) chỉ để thử nghiệm, chưa gắn frontend/backend.
- Model v2 hướng tới **nhà phố** TP.HCM, không phải chung cư / đất nền nói chung.
- Ảnh tin seed tải từ Unsplash; nếu mạng chặn, tin vẫn tạo được nhưng có thể không có ảnh.

Hết.
