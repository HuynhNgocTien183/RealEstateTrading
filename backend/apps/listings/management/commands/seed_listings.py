import random
import urllib.request
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.listings.models import Listing, ListingImage

User = get_user_model()

# Phân nhóm Quận theo khoảng đơn giá (triệu VNĐ / m2 sàn cơ bản) sát với dữ liệu thực tế
DISTRICT_PRICE_PER_M2 = {
    # Nhóm Trung tâm & Cận trung tâm (120 - 220 triệu/m2)
    'Quận 1': (150, 250),
    'Quận 3': (130, 220),
    'Phú Nhuận': (110, 180),
    'Quận 10': (100, 170),
    'Bình Thạnh': (90, 150),
    'Tân Bình': (85, 140),

    # Nhóm Đang phát triển / Nội thành mở rộng (60 - 110 triệu/m2)
    'Quận 7': (70, 120),
    'Quận 4': (75, 125),
    'Quận 5': (80, 130),
    'Quận 6': (65, 105),
    'Quận 8': (55, 95),
    'Quận 11': (70, 115),
    'Gò Vấp': (65, 110),
    'Tân Phú': (60, 100),
    'Bình Tân': (50, 85),
    'Thành phố Thủ Đức': (55, 105),

    # Nhóm Ngoại thành / Ven đô (25 - 60 triệu/m2)
    'Quận 12': (45, 75),
    'Hóc Môn': (30, 55),
    'Nhà Bè': (35, 65),
    'Bình Chánh': (25, 50),
    'Củ Chi': (18, 35),
    'Cần Giờ': (15, 30),
}

DISTRICTS = list(DISTRICT_PRICE_PER_M2.keys())

STREET_NAMES = [
    'Nguyễn Văn Linh', 'Lê Văn Việt', 'Phạm Văn Đồng', 'Nguyễn Thị Minh Khai',
    'Điện Biên Phủ', 'Cách Mạng Tháng Tám', 'Nguyễn Trãi', 'Trần Hưng Đạo',
    'Quang Trung', 'Nguyễn Oanh', 'Lê Trọng Tấn', 'Huỳnh Tấn Phát',
    'Đỗ Xuân Hợp', 'Nguyễn Duy Trinh', 'Lê Văn Sỹ', 'Phan Xích Long',
    'Bùi Đình Túy', 'Tân Kỳ Tân Quý', 'Trường Chinh', 'Dương Quảng Hàm'
]

PROPERTY_TYPES = ['house', 'apartment', 'land', 'villa']
PROPERTY_TYPE_LABELS = {
    'house': 'Nhà phố',
    'apartment': 'Chung cư',
    'land': 'Đất nền',
    'villa': 'Biệt thự',
}

# Hệ số điều chỉnh giá theo loại hình bất động sản
PROPERTY_TYPE_PRICE_MULTIPLIER = {
    'land': 0.85,  # Đất chưa xây dựng
    'apartment': 0.70,  # Chung cư (tính trên diện tích thông thủy)
    'house': 1.0,  # Nhà phố tiêu chuẩn
    'villa': 1.45,  # Biệt thự cao cấp
}

TITLE_TEMPLATES = [
    "{type} {district} - Giá tốt, sổ hồng riêng",
    "{type} mặt tiền {district}, vị trí đắc địa",
    "Bán gấp {type} {district}, {area}m²",
    "{type} khu dân cư an ninh {district}",
    "{type} view đẹp, vị trí đẹp tại {district}",
]

DESCRIPTION_TEMPLATES = [
    "Bất động sản vị trí đẹp, gần chợ, trường học, bệnh viện. Pháp lý rõ ràng, sổ hồng chính chủ.",
    "Nhà mới xây, thiết kế hiện đại, nội thất cao cấp. Khu vực an ninh, dân trí cao.",
    "Vị trí thuận tiện di chuyển vào trung tâm thành phố, gần các tuyến đường lớn.",
    "Diện tích rộng rãi, thoáng mát, phù hợp cho gia đình hoặc đầu tư cho thuê.",
    "Giá bán thương lượng nhẹ cho khách thiện chí, hỗ trợ vay ngân hàng tối đa.",
]

# Bộ sưu tập Photo ID ảnh bất động sản từ Unsplash
REAL_ESTATE_IMAGES = {
    'house': [
        '1568605117036-5fe5e7bab0b7',  # Mặt tiền nhà phố
        '1570129477492-45c003edd2be',  # Nhà phố phong cách đương đại
        '1583608205776-bfd35f0d9f83',  # Nhà phố mới xây
        '1600585154340-be6161a56a0c',  # Nhà hiện đại có sân
        '1513694203232-719a280e022f',  # Góc phòng khách nhà phố
    ],
    'villa': [
        '1600596542815-ffad4c1539a9',  # Biệt thự vườn
        '1512917774080-9991f1c4c750',  # Biệt thự hồ bơi
        '1613490493576-7fde63acd811',  # Biệt thự ven hồ
        '1600607687939-ce8a6c25118c',  # Biệt thự thiết kế mở
        '1600585152220-90363fe7e115',  # Sân sau biệt thự
    ],
    'apartment': [
        '1502672260266-1c1ef2d93688',  # Căn hộ chung cư cao cấp
        '1560448204-e02f11c3d0e2',  # Phòng khách chung cư
        '1522708323590-d24dbb6b0267',  # Căn hộ ấm cúng
        '1567767299-fc5b42a98f12',  # Chung cư view thành phố
        '1545324418-cc1a3fa10c00',  # Ban công chung cư
    ],
    'land': [
        '1500382017468-9049fed747ef',  # Đất nền phân lô
        '1524813686514-a57563d77d4c',  # Lô đất quy hoạch đẹp
        '1500534623283-312aade485b7',  # Khu đất view thoáng
        '1500076656116-558758c991c1',  # Đất vườn / ven đô
    ],
    'interior': [
        '1600566753190-17f0baa2a6c3',  # Gian bếp hiện đại
        '1616486338812-3dadae4b4ace',  # Phòng ngủ
        '1584622650111-993a426fbf0a',  # Phòng tắm sang trọng
        '1556911220-e15b29be8c8f',  # Phòng ăn
    ]
}


class Command(BaseCommand):
    help = "Tạo tin đăng bất động sản mẫu với mức giá thị trường thực tế TPHCM."

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=30, help='Số lượng tin cần tạo')
        parser.add_argument('--with-images', action='store_true', default=True,
                            help='Tải kèm ảnh nhà thực tế từ Unsplash')
        parser.add_argument('--clear', action='store_true',
                            help='Xóa toàn bộ tin đăng và ảnh cũ trước khi tạo mới')

    def _calculate_realistic_price(self, district, property_type, area, floors):
        """
        Tính toán giá bán thực tế dựa trên vị trí, diện tích, số tầng và phân khúc.
        Đơn vị trả về: VNĐ (làm tròn đến hàng chục triệu).
        """
        min_rate, max_rate = DISTRICT_PRICE_PER_M2.get(district, (40, 70))
        base_rate_per_m2 = random.uniform(min_rate, max_rate)  # Triệu VNĐ / m2

        # Tính toán giá đất cơ bản
        total_price_mil = area * base_rate_per_m2

        # Điều chỉnh theo số tầng đối với nhà phố / biệt thự
        if property_type in ['house', 'villa'] and floors and floors > 1:
            total_price_mil += (floors - 1) * (area * 0.25 * base_rate_per_m2)

        # Nhân hệ số loại hình BĐS
        multiplier = PROPERTY_TYPE_PRICE_MULTIPLIER.get(property_type, 1.0)
        total_price_mil *= multiplier

        # Chuyển sang đơn vị VNĐ và làm tròn đến 50.000.000 VNĐ
        raw_price_vnd = total_price_mil * 1_000_000
        rounded_price = round(raw_price_vnd / 50_000_000) * 50_000_000

        # Giữ khoảng giá an toàn (tối thiểu 1.2 tỷ)
        return max(int(rounded_price), 1_200_000_000)

    def handle(self, *args, **options):
        count = options['count']
        with_images = options['with_images']
        clear_old = options['clear']

        if clear_old:
            deleted_count, _ = Listing.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Đã xóa {deleted_count} bản ghi tin đăng/ảnh cũ."))

        sellers = list(User.objects.filter(role='seller'))
        if not sellers:
            self.stderr.write(self.style.ERROR(
                "Không tìm thấy tài khoản nào có role='seller'. "
                "Tạo ít nhất 1 seller trước khi chạy lệnh này."
            ))
            return

        self.stdout.write(f"Tìm thấy {len(sellers)} seller. Bắt đầu tạo {count} tin đăng...")

        created = 0
        for i in range(count):
            seller = random.choice(sellers)
            district = random.choice(DISTRICTS)
            property_type = random.choice(PROPERTY_TYPES)
            street = random.choice(STREET_NAMES)
            house_number = random.randint(1, 500)

            # Diện tích tùy biến theo loại hình
            if property_type == 'apartment':
                area = random.randint(45, 110)
                floors = None
            elif property_type == 'villa':
                area = random.randint(120, 300)
                floors = random.randint(2, 4)
            elif property_type == 'land':
                area = random.randint(50, 200)
                floors = None
            else:  # house
                area = random.randint(35, 120)
                floors = random.randint(1, 5)

            # Tính giá thực tế
            price_vnd = self._calculate_realistic_price(district, property_type, area, floors)

            title = random.choice(TITLE_TEMPLATES).format(
                type=PROPERTY_TYPE_LABELS[property_type],
                district=district,
                area=area,
            )
            description = random.choice(DESCRIPTION_TEMPLATES)

            listing = Listing.objects.create(
                seller=seller,
                title=title,
                description=description,
                price=price_vnd,
                area=area,
                floors=floors,
                bedrooms=random.randint(1, 5) if property_type != 'land' else 0,
                bathrooms=random.randint(1, 5) if property_type != 'land' else 0,
                property_type=property_type,
                address=f"{house_number} Đường {street}, {district}",
                city='Hồ Chí Minh',
                district=district,
                latitude=round(random.uniform(10.70, 10.88), 6),
                longitude=round(random.uniform(106.60, 106.78), 6),
                status=Listing.Status.AVAILABLE,
                approval_status=Listing.ApprovalStatus.APPROVED,
                views_count=random.randint(5, 300),
            )

            if with_images:
                self._attach_placeholder_image(listing, property_type)

            created += 1
            price_in_billion = price_vnd / 1_000_000_000
            self.stdout.write(f"  [{created}/{count}] Đã tạo: {title} - Giá: {price_in_billion:.2f} tỷ")

        self.stdout.write(self.style.SUCCESS(f"\n✓ Hoàn tất! Đã tạo {created} tin đăng mẫu."))

    def _attach_placeholder_image(self, listing, property_type):
        """Tải tối thiểu 2 ảnh (tối đa 4 ảnh) từ Unsplash, đảm bảo không trùng lặp trong cùng 1 tin."""
        num_images = random.randint(2, 4)

        primary_pool = REAL_ESTATE_IMAGES.get(property_type, REAL_ESTATE_IMAGES['house'])
        interior_pool = REAL_ESTATE_IMAGES['interior'] if property_type != 'land' else primary_pool

        # Kết hợp pool ngoại thất và nội thất để tạo danh sách ảnh đa dạng
        combined_pool = list(set(primary_pool + interior_pool))
        num_to_pick = min(num_images, len(combined_pool))
        selected_ids = random.sample(combined_pool, num_to_pick)

        for img_index, photo_id in enumerate(selected_ids):
            url = f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w=800&h=600&q=80"
            try:
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    image_data = response.read()

                image_file = ContentFile(
                    image_data,
                    name=f"listing_{listing.id}_{img_index + 1}.jpg"
                )
                ListingImage.objects.create(
                    listing=listing,
                    image=image_file,
                    is_primary=(img_index == 0),
                )
            except Exception as e:
                self.stderr.write(self.style.WARNING(
                    f"    ⚠ Không tải được ảnh {img_index + 1} cho tin '{listing.title}': {e}"
                ))