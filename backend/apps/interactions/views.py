from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from apps.listings.cache_utils import invalidate_listing_cache

from .models import Favorite
from .serializers import  FavoriteSerializer

class FavoriteViewSet(viewsets.ModelViewSet):

    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        listing_id = request.data.get('listing')
        favorite, created = Favorite.objects.get_or_create(
            user=request.user, listing_id=listing_id
        )
        if not created:
            return Response(
                {"detail": "Tin này đã có trong danh sách yêu thích."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        invalidate_listing_cache(listing_id)
        return Response(FavoriteSerializer(favorite).data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        listing_id = instance.listing_id
        instance.delete()
        invalidate_listing_cache(listing_id)