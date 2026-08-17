from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q

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
        return Response(FavoriteSerializer(favorite).data, status=status.HTTP_201_CREATED)