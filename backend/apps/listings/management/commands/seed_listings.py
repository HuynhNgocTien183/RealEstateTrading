import random
import urllib.request
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.listings.models import Listing, ListingImage

User = get_user_model()

DATASET_LISTINGS = [
    {"address": "Hẻm 555, Đường Trần Hưng Đạo, Phường Cầu Kho, Quận 1, Hồ Chí Minh", "area": 35, "frontage": 3, "access_road": 6, "floors": 3, "bedrooms": 2, "bathrooms": 2, "legal_status": "Have certificate", "furniture": "Basic", "price": 5.70, "property_type": "house"},
    {"address": "Hẻm 38/, Đường Trần Khắc Chân, Phường Tân Định, Quận 1, Hồ Chí Minh", "area": 48, "frontage": 6, "access_road": 5, "floors": 3, "bedrooms": 6, "bathrooms": 3, "legal_status": "Have certificate", "furniture": "Basic", "price": 8.90, "property_type": "house"},
    {"address": "Đường Lê Văn Sỹ, Phường 12, Quận 3, Hồ Chí Minh", "area": 32, "frontage": 4, "access_road": 3, "floors": 2, "bedrooms": 2, "bathrooms": 3, "legal_status": "Have certificate", "furniture": "Full", "price": 5.20, "property_type": "house"},
    {"address": "Đường Nguyễn Thiện Thuật, Phường 1, Quận 3, Hồ Chí Minh", "area": 46, "frontage": 3.1, "access_road": 5, "floors": 4, "bedrooms": 6, "bathrooms": 6, "legal_status": "Have certificate", "furniture": "Basic", "price": 8.50, "property_type": "house"},
    {"address": "Đường Tôn Đản, Phường 10, Quận 4, Hồ Chí Minh", "area": 32, "frontage": 5, "access_road": 3, "floors": 4, "bedrooms": 3, "bathrooms": 3, "legal_status": "Have certificate", "furniture": "Full", "price": 3.90, "property_type": "house"},
    {"address": "Đường Vĩnh Hội, Phường 4, Quận 4, Hồ Chí Minh", "area": 40, "frontage": 4, "access_road": 8, "floors": 4, "bedrooms": 3, "bathrooms": 3, "legal_status": "Have certificate", "furniture": "Full", "price": 8.39, "property_type": "house"},
    {"address": "Đường Trần Phú, Phường 4, Quận 5, Hồ Chí Minh", "area": 35, "frontage": 3.5, "access_road": 5, "floors": 5, "bedrooms": 5, "bathrooms": 6, "legal_status": "Have certificate", "furniture": "Full", "price": 9.50, "property_type": "house"},
    {"address": "Đường Đặng Nguyên Cẩn, Phường 14, Quận 6, Hồ Chí Minh", "area": 60, "frontage": 4, "access_road": 5, "floors": 2, "bedrooms": 3, "bathrooms": 3, "legal_status": "Have certificate", "furniture": "Full", "price": 5.80, "property_type": "house"},
    {"address": "Đường Cư Xá Phú Lâm A, Phường 12, Quận 6, Hồ Chí Minh", "area": 84.4, "frontage": 5.5, "access_road": 4.5, "floors": 3, "bedrooms": 4, "bathrooms": 6, "legal_status": "Have certificate", "furniture": "Full", "price": 8.90, "property_type": "house"},
    {"address": "793 Trần Xuân Soạn, Phường Tân Hưng, Quận 7, Hồ Chí Minh", "area": 45.9, "frontage": 3.25, "access_road": 5, "floors": 2, "bedrooms": 3, "bathrooms": 2, "legal_status": "Have certificate", "furniture": "Full", "price": 5.20, "property_type": "house"},
    {"address": "Đường Nguyễn Thị Thập, Phường Tân Quy, Quận 7, Hồ Chí Minh", "area": 100, "frontage": 5, "access_road": 5, "floors": 4, "bedrooms": 4, "bathrooms": 4, "legal_status": "Have certificate", "furniture": "Full", "price": 8.50, "property_type": "house"},
    {"address": "Đường Tùng Thiện Vương, Phường 11, Quận 8, Hồ Chí Minh", "area": 50, "frontage": 3.7, "access_road": 14, "floors": 4, "bedrooms": 3, "bathrooms": 3, "legal_status": "Have certificate", "furniture": "Full", "price": 7.00, "property_type": "house"},
    {"address": "Đường Nguyễn Duy Trinh, Phường Long Trường, Quận 9, Hồ Chí Minh", "area": 60, "frontage": 5.2, "access_road": 5, "floors": 3, "bedrooms": 4, "bathrooms": 3, "legal_status": "Have certificate", "furniture": "Full", "price": 4.50, "property_type": "house"},
    {"address": "Đường Số 339, Phường Phước Long B, Quận 9, Hồ Chí Minh", "area": 88, "frontage": 4, "access_road": 4, "floors": 3, "bedrooms": 3, "bathrooms": 2, "legal_status": "Have certificate", "furniture": "Full", "price": 7.20, "property_type": "house"},
    {"address": "Đường Vĩnh Viễn, Phường 5, Quận 10, Hồ Chí Minh", "area": 37, "frontage": 4, "access_road": 3, "floors": 3, "bedrooms": 4, "bathrooms": 4, "legal_status": "Have certificate", "furniture": "Full", "price": 5.60, "property_type": "house"},
    {"address": "163, Đường Tô Hiến Thành, Phường 13, Quận 10, Hồ Chí Minh", "area": 54, "frontage": 3, "access_road": 12, "floors": 2, "bedrooms": 2, "bathrooms": 2, "legal_status": "Have certificate", "furniture": "Basic", "price": 8.80, "property_type": "house"},
    {"address": "Đường Lạc Long Quân, Phường 5, Quận 11, Hồ Chí Minh", "area": 58, "frontage": 4, "access_road": 4, "floors": 2, "bedrooms": 2, "bathrooms": 2, "legal_status": "Have certificate", "furniture": "Basic", "price": 4.99, "property_type": "house"},
    {"address": "Đường Lãnh Binh Thăng, Phường 12, Quận 11, Hồ Chí Minh", "area": 45, "frontage": 3.5, "access_road": 4, "floors": 4, "bedrooms": 4, "bathrooms": 4, "legal_status": "Have certificate", "furniture": "Full", "price": 8.00, "property_type": "house"},
    {"address": "391//, Đường Nguyễn Văn Quá, Phường Đông Hưng Thuận, Quận 12, Hồ Chí Minh", "area": 68, "frontage": 4, "access_road": 3, "floors": 2, "bedrooms": 2, "bathrooms": 2, "legal_status": "Have certificate", "furniture": "Basic", "price": 3.79, "property_type": "house"},
    {"address": "Đường Nguyễn Tư Giản, Phường 12, Gò Vấp, Hồ Chí Minh", "area": 45.1, "frontage": 4, "access_road": 4, "floors": 3, "bedrooms": 6, "bathrooms": 6, "legal_status": "Have certificate", "furniture": "Full", "price": 5.48, "property_type": "house"},
    {"address": "Đường Số 8, Phường 11, Gò Vấp, Hồ Chí Minh", "area": 56, "frontage": 4.1, "access_road": 6, "floors": 5, "bedrooms": 5, "bathrooms": 5, "legal_status": "Have certificate", "furniture": "Full", "price": 7.80, "property_type": "house"},
    {"address": "Đường Trần Quý Cáp, Phường 11, Bình Thạnh, Hồ Chí Minh", "area": 51.1, "frontage": 4, "access_road": 3, "floors": 2, "bedrooms": 3, "bathrooms": 2, "legal_status": "Have certificate", "furniture": "Full", "price": 5.69, "property_type": "house"},
    {"address": "Đường Nguyễn Lâm, Phường 3, Bình Thạnh, Hồ Chí Minh", "area": 50, "frontage": 4.1, "access_road": 5, "floors": 4, "bedrooms": 4, "bathrooms": 5, "legal_status": "Have certificate", "furniture": "Basic", "price": 8.80, "property_type": "house"},
    {"address": "Đường Huỳnh Văn Bánh, Phường 17, Phú Nhuận, Hồ Chí Minh", "area": 67, "frontage": 5, "access_road": 3, "floors": 3, "bedrooms": 3, "bathrooms": 3, "legal_status": "Have certificate", "furniture": "Full", "price": 6.90, "property_type": "house"},
    {"address": "241a/, Đường Huỳnh Văn Bánh, Phường 12, Phú Nhuận, Hồ Chí Minh", "area": 73, "frontage": 5.4, "access_road": 3, "floors": 4, "bedrooms": 4, "bathrooms": 4, "legal_status": "Have certificate", "furniture": "Full", "price": 8.90, "property_type": "house"},
    {"address": "86, Đường Trường Chinh, Phường 12, Tân Bình, Hồ Chí Minh", "area": 53, "frontage": 3.6, "access_road": 5, "floors": 4, "bedrooms": 3, "bathrooms": 4, "legal_status": "Have certificate", "furniture": "Basic", "price": 6.50, "property_type": "house"},
    {"address": "Đường Cách Mạng Tháng Tám, Phường 5, Tân Bình, Hồ Chí Minh", "area": 48, "frontage": 3.3, "access_road": 6, "floors": 4, "bedrooms": 4, "bathrooms": 5, "legal_status": "Have certificate", "furniture": "Full", "price": 8.50, "property_type": "house"},
    {"address": "Đường Nguyễn Hữu Dật, Phường Tây Thạnh, Tân Phú, Hồ Chí Minh", "area": 76, "frontage": 4, "access_road": 5, "floors": 2, "bedrooms": 3, "bathrooms": 2, "legal_status": "Have certificate", "furniture": "Basic", "price": 6.50, "property_type": "house"},
    {"address": "Đường Số 55A, Phường Tân Tạo, Bình Tân, Hồ Chí Minh", "area": 64, "frontage": 4, "access_road": 10, "floors": 3, "bedrooms": 3, "bathrooms": 3, "legal_status": "Have certificate", "furniture": "Full", "price": 5.65, "property_type": "house"},
    {"address": "Đường Quốc Lộ 13, Phường Hiệp Bình Phước, Thủ Đức, Hồ Chí Minh", "area": 57.3, "frontage": 4, "access_road": 7, "floors": 4, "bedrooms": 4, "bathrooms": 5, "legal_status": "Have certificate", "furniture": "Full", "price": 6.50, "property_type": "house"},
]

PROPERTY_TYPE_LABELS = {
    "house": "Nhà phố",
    "apartment": "Chung cư",
    "land": "Đất nền",
    "villa": "Biệt thự",
}

TITLE_TEMPLATES = [
    "{type} {district} - {area}m², {floors} tầng",
    "Bán {type} {district}, {bedrooms} PN, sổ hồng",
    "{type} tại {district} - Giá {price:.2f} tỷ",
    "Bán nhà {district}, mặt tiền {frontage}m",
]

LEGAL_LABELS = {
    "Have certificate": "sổ hồng",
    "Sale contract": "hợp đồng mua bán",
    "Waiting": "đang chờ sổ",
}

FURNITURE_LABELS = {
    "Full": "đầy đủ nội thất",
    "Basic": "nội thất cơ bản",
    "Empty": "nhà trống",
}

REAL_ESTATE_IMAGES = {
    "house": [
        "1568605117036-5fe5e7bab0b7",
        "1570129477492-45c003edd2be",
        "1583608205776-bfd35f0d9f83",
        "1600585154340-be6161a56a0c",
        "1513694203232-719a280e022f",
    ],
    "apartment": [
        "1502672260266-1c1ef2d93688",
        "1560448204-e02f11c3d0e2",
        "1522708323590-d24dbb6b0267",
        "1567767299-fc5b42a98f12",
        "1545324418-cc1a3fa10c00",
    ],
    "interior": [
        "1600566753190-17f0baa2a6c3",
        "1616486338812-3dadae4b4ace",
        "1584622650111-993a426fbf0a",
        "1556911220-e15b29be8c8f",
    ],
}


def get_district(address):
    parts = [x.strip() for x in address.split(",") if x.strip()]
    if len(parts) >= 2:
        return parts[-2]
    return "Khác"


def build_description(data):
    legal = LEGAL_LABELS.get(data["legal_status"], data["legal_status"])
    furniture = FURNITURE_LABELS.get(data["furniture"], data["furniture"])
    return (
        f"Nhà phố {data['area']}m² tại {data['address']}. "
        f"{data['floors']} tầng, {data['bedrooms']} phòng ngủ, {data['bathrooms']} phòng tắm. "
        f"Mặt tiền {data['frontage']}m, đường/hẻm {data['access_road']}m. "
        f"Pháp lý {legal}, {furniture}. "
        f"Nguồn dữ liệu: DuLieuGiaNhaHCM2024."
    )


class Command(BaseCommand):
    help = "Tạo 30 tin nhà phố đủ số liệu từ DuLieuGiaNhaHCM2024.csv."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=30, help="Số lượng tin cần tạo, tối đa 30")
        parser.add_argument("--with-images", action="store_true", default=True, help="Tải ảnh từ Unsplash")
        parser.add_argument("--clear", action="store_true", help="Xóa toàn bộ tin đăng và ảnh cũ trước khi tạo")

    def handle(self, *args, **options):
        count = min(options["count"], len(DATASET_LISTINGS))
        with_images = options["with_images"]

        if options["clear"]:
            deleted_count, _ = Listing.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Đã xóa {deleted_count} bản ghi tin đăng/ảnh cũ."))

        sellers = list(User.objects.filter(role="seller"))
        if not sellers:
            self.stderr.write(self.style.ERROR("Không tìm thấy tài khoản nào có role='seller'. Tạo ít nhất 1 seller trước."))
            return

        self.stdout.write(f"Tìm thấy {len(sellers)} seller. Bắt đầu tạo {count} tin từ dataset 2024...")

        created = 0
        for data in DATASET_LISTINGS[:count]:
            seller = random.choice(sellers)
            district = get_district(data["address"])
            price_vnd = int(round(data["price"] * 1_000_000_000))
            property_type = data["property_type"]

            title = random.choice(TITLE_TEMPLATES).format(
                type=PROPERTY_TYPE_LABELS[property_type],
                district=district,
                area=data["area"],
                floors=data["floors"],
                bedrooms=data["bedrooms"],
                frontage=data["frontage"],
                price=data["price"],
            )
            description = build_description(data)

            listing = Listing.objects.create(
                seller=seller,
                title=title,
                description=description,
                price=price_vnd,
                area=data["area"],
                floors=data["floors"],
                bedrooms=data["bedrooms"],
                bathrooms=data["bathrooms"],
                property_type=property_type,
                address=data["address"],
                city="Hồ Chí Minh",
                district=district,
                latitude=round(random.uniform(10.70, 10.88), 6),
                longitude=round(random.uniform(106.60, 106.78), 6),
                status=Listing.Status.AVAILABLE,
                approval_status=Listing.ApprovalStatus.APPROVED,
                views_count=random.randint(5, 300),
            )

            if with_images:
                self._attach_images(listing, property_type)

            created += 1
            self.stdout.write(
                f"  [{created}/{count}] {district} | {data['area']}m² | "
                f"{data['floors']} tầng | MT {data['frontage']}m | "
                f"{data['price']:.2f} tỷ | {data['address']}"
            )

        self.stdout.write(self.style.SUCCESS(f"\n✓ Hoàn tất! Đã tạo {created} tin đăng từ DuLieuGiaNhaHCM2024."))

    def _attach_images(self, listing, property_type):
        primary_pool = REAL_ESTATE_IMAGES.get(property_type, REAL_ESTATE_IMAGES["house"])
        combined_pool = list(dict.fromkeys(primary_pool + REAL_ESTATE_IMAGES["interior"]))
        selected_ids = random.sample(combined_pool, min(random.randint(2, 4), len(combined_pool)))

        for img_index, photo_id in enumerate(selected_ids):
            url = f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w=800&h=600&q=80"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as response:
                    image_data = response.read()

                image_file = ContentFile(image_data, name=f"listing_{listing.id}_{img_index + 1}.jpg")
                ListingImage.objects.create(
                    listing=listing,
                    image=image_file,
                    is_primary=(img_index == 0),
                )
            except Exception as e:
                self.stderr.write(self.style.WARNING(f"  ⚠ Không tải được ảnh: {e}"))
