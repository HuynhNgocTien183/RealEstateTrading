import random
import urllib.request
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.listings.models import Listing, ListingImage

User = get_user_model()

DISTRICTS = [
    'Quận 1', 'Quận 3', 'Quận 4', 'Quận 5', 'Quận 6', 'Quận 7',
    'Quận 8', 'Quận 10', 'Quận 11', 'Quận 12',
    'Bình Thạnh', 'Phú Nhuận', 'Tân Bình', 'Tân Phú',
    'Gò Vấp', 'Bình Tân', 'Thành phố Thủ Đức',
    'Bình Chánh', 'Hóc Môn', 'Củ Chi', 'Nhà Bè', 'Cần Giờ',
]

STREET_NAMES = [
    'Nguyễn Văn Linh', 'Lê Văn Việt', 'Phạm Văn Đồng', 'Nguyễn Thị Minh Khai',
    'Điện Biên Phủ', 'Cách Mạng Tháng Tám', 'Nguyễn Trãi', 'Trần Hưng Đạo',
    'Quang Trung', 'Nguyễn Oanh', 'Lê Trọng Tấn', 'Huỳnh Tấn Phát',
    'Đỗ Xuân Hợp', 'Nguyễn Duy Trinh', 'Số 22',
]

PROPERTY_TYPES = ['house', 'apartment', 'land', 'villa']
PROPERTY_TYPE_LABELS = {
    'house': 'Nhà phố', 'apartment': 'Chung cư', 'land': 'Đất nền', 'villa': 'Biệt thự',
}

TITLE_TEMPLATES = [
    "{type} {district} - Giá tốt, sổ hồng riêng",
    "{type} mặt tiền {district}, vị trí đắc địa",
    "Bán gấp {type} {district}, {area}m²",
    "{type} khu dân cư an ninh {district}",
    "{type} view đẹp, gần trường học tại {district}",
]

DESCRIPTION_TEMPLATES = [
    "Bất động sản vị trí đẹp, gần chợ, trường học, bệnh viện. Pháp lý rõ ràng, sổ hồng chính chủ.",
    "Nhà mới xây, thiết kế hiện đại, nội thất cao cấp. Khu vực an ninh, dân trí cao.",
    "Vị trí thuận tiện di chuyển vào trung tâm thành phố, gần các tuyến đường lớn.",
    "Diện tích rộng rãi, thoáng mát, phù hợp cho gia đình hoặc đầu tư cho thuê.",
    "Giá bán thương lượng nhẹ cho khách thiện chí, hỗ trợ vay ngân hàng tối đa.",
]


class Command(BaseCommand):
    help = "Tạo 30 tin đăng bất động sản mẫu (approved), gán ngẫu nhiên cho các seller đã có."

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=30, help='Số lượng tin cần tạo')
        parser.add_argument('--with-images', action='store_true', default=True,
                             help='Tải kèm ảnh placeholder từ Lorem Picsum')

    def handle(self, *args, **options):
        count = options['count']
        with_images = options['with_images']

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
            area = random.randint(30, 300)

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
                price=random.randint(1, 25) * 100_000_000 + random.choice([0, 50_000_000]),
                area=area,
                floors=random.randint(1, 5) if property_type in ['house', 'villa'] else None,
                bedrooms=random.randint(1, 6),
                bathrooms=random.randint(1, 4),
                property_type=property_type,
                address=f"{house_number} Đường {street}, {district}",
                city='Hồ Chí Minh',
                district=district,
                latitude=round(random.uniform(10.35, 10.90), 6),
                longitude=round(random.uniform(106.35, 106.90), 6),
                status=Listing.Status.AVAILABLE,
                approval_status=Listing.ApprovalStatus.APPROVED,
                views_count=random.randint(0, 200),
            )

            if with_images:
                self._attach_placeholder_image(listing, i)

            created += 1
            self.stdout.write(f"  [{created}/{count}] Đã tạo: {title}")

        self.stdout.write(self.style.SUCCESS(f"\n✓ Hoàn tất! Đã tạo {created} tin đăng mẫu."))

    def _attach_placeholder_image(self, listing, seed):
        """Tải 1-2 ảnh placeholder ngẫu nhiên từ Lorem Picsum, gắn vào tin đăng."""
        num_images = random.choice([1, 1, 2])
        for img_index in range(num_images):
            url = f"https://picsum.photos/seed/listing{seed}_{img_index}/800/600"
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    image_data = response.read()

                image_file = ContentFile(image_data, name=f'seed_listing_{seed}_{img_index}.jpg')
                ListingImage.objects.create(
                    listing=listing,
                    image=image_file,
                    is_primary=(img_index == 0),
                )
            except Exception as e:
                self.stderr.write(self.style.WARNING(
                    f"    ⚠ Không tải được ảnh cho tin '{listing.title}': {e}"
                ))