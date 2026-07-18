from rest_framework import serializers
from .models import Listing, ListingImage


class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ('id', 'image', 'is_primary', 'uploaded_at')


class ListingSerializer(serializers.ModelSerializer):
    images = ListingImageSerializer(many=True, read_only=True)
    seller_username = serializers.CharField(source='seller.username', read_only=True)

    class Meta:
        model = Listing
        fields = (
            'id', 'seller', 'seller_username', 'title', 'description',
            'price', 'area', 'bedrooms', 'bathrooms', 'property_type',
            'address', 'city', 'district', 'latitude', 'longitude',
            'status', 'predicted_price', 'views_count',
            'images', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'seller', 'predicted_price', 'views_count', 'created_at', 'updated_at')


class ListingCreateSerializer(serializers.ModelSerializer):
    """Serializer riêng cho tạo/sửa tin — không cần hiển thị các field read-only."""
    class Meta:
        model = Listing
        fields = (
            'title', 'description', 'price', 'area', 'bedrooms', 'bathrooms',
            'property_type', 'address', 'city', 'district', 'latitude', 'longitude',
            'status',
        )