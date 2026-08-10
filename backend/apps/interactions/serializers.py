from rest_framework import serializers
from .models import Favorite
from apps.listings.serializers import ListingSerializer


class FavoriteSerializer(serializers.ModelSerializer):
    listing_detail = ListingSerializer(source='listing', read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'listing', 'listing_detail', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')