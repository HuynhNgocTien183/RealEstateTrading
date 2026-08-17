from rest_framework import serializers
from .models import Listing, ListingImage


class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ('id', 'image', 'is_primary', 'uploaded_at')


class ListingSerializer(serializers.ModelSerializer):
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    seller_full_name = serializers.CharField(source='seller.full_name', read_only=True)
    seller_phone = serializers.CharField(source='seller.phone', read_only=True)
    seller_email = serializers.CharField(source='seller.email', read_only=True)
    images = ListingImageSerializer(many=True, read_only=True)
    maps_link = serializers.ReadOnlyField()
    favorites_count = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = (
            'id', 'seller', 'seller_username', 'seller_full_name', 'seller_phone', 'seller_email',
            'title', 'description',
            'price', 'area', 'floors', 'bedrooms', 'bathrooms', 'property_type',
            'address', 'city', 'district', 'latitude', 'longitude',
            'google_maps_url', 'maps_link', 'favorites_count',
            'status', 'approval_status', 'rejection_reason',
            'predicted_price', 'views_count',
            'images', 'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'seller', 'approval_status', 'rejection_reason',
            'reviewed_at', 'reviewed_by', 'predicted_price', 'views_count',
            'created_at', 'updated_at',
        )

    def get_favorites_count(self, obj):
        return obj.favorited_by.count()


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
            'title', 'description', 'price', 'area', 'floors', 'bedrooms', 'bathrooms',
            'property_type', 'address', 'city', 'district', 'latitude', 'longitude',
            'google_maps_url', 'status',
        )
