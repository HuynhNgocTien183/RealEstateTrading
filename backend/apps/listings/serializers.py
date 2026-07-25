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
            'status', 'approval_status', 'rejection_reason',   # thêm 2 field mới
            'predicted_price', 'views_count',
            'images', 'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'seller', 'approval_status', 'rejection_reason',
            'reviewed_at', 'reviewed_by', 'predicted_price', 'views_count',
            'created_at', 'updated_at',
        )


# Thêm serializer riêng cho admin duyệt bài
class ListingReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ('approval_status', 'rejection_reason')


class ListingCreateSerializer(serializers.ModelSerializer):
    """Serializer riêng cho tạo/sửa tin — không cần hiển thị các field read-only."""
    class Meta:
        model = Listing
        fields = (
            'title', 'description', 'price', 'area', 'bedrooms', 'bathrooms',
            'property_type', 'address', 'city', 'district', 'latitude', 'longitude',
            'status',
        )
