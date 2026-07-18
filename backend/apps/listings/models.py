from django.db import models
from django.conf import settings


class Listing(models.Model):
    class PropertyType(models.TextChoices):
        HOUSE = 'house', 'Nhà phố'
        APARTMENT = 'apartment', 'Chung cư'
        LAND = 'land', 'Đất nền'
        VILLA = 'villa', 'Biệt thự'

    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Đang bán'
        SOLD = 'sold', 'Đã bán'
        HIDDEN = 'hidden', 'Đã ẩn'

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings',
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=15, decimal_places=2)
    area = models.DecimalField(max_digits=10, decimal_places=2, help_text="Diện tích (m²)")
    bedrooms = models.PositiveSmallIntegerField(default=0)
    bathrooms = models.PositiveSmallIntegerField(default=0)

    property_type = models.CharField(
        max_length=20, choices=PropertyType.choices, default=PropertyType.HOUSE
    )

    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.AVAILABLE
    )

    predicted_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )

    views_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.price:,.0f} VNĐ"


class ListingImage(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='images'
    )
    image = models.ImageField(upload_to='listingImages/%Y/%m/')
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'uploaded_at']

    def __str__(self):
        return f"Ảnh của {self.listing.title}"