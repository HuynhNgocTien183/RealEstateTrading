import hashlib
from django.conf import settings
from django.core.cache import cache
from django.db.models import F, Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .cache_utils import invalidate_listing_cache
from .filters import ListingFilter
from .models import Listing, ListingImage
from .permissions import IsAdminUser, IsSellerOrReadOnly
from .serializers import ListingCreateSerializer, ListingSerializer


class ListingViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsSellerOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ListingFilter
    search_fields = ['title', 'description', 'address']
    ordering_fields = ['price', 'area', 'created_at']

    # ===== QUERYSET theo quyền hạn =====
    def get_queryset(self):
        user = self.request.user

        # Public list: chỉ hiển thị tin APPROVED + AVAILABLE
        if self.action == 'list':
            return Listing.objects.filter(
                approval_status=Listing.ApprovalStatus.APPROVED,
                status=Listing.Status.AVAILABLE,
            )

        # Các action khác (retrieve/update/destroy)
        if user.is_authenticated and user.is_staff:
            return Listing.objects.all()

        if user.is_authenticated:
            return Listing.objects.filter(
                Q(approval_status=Listing.ApprovalStatus.APPROVED) | Q(seller=user)
            )

        return Listing.objects.filter(
            approval_status=Listing.ApprovalStatus.APPROVED,
            status=Listing.Status.AVAILABLE,
        )

    # ===== SERIALIZER theo action =====
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ListingCreateSerializer
        return ListingSerializer

    # ===== REDIS CACHE HELPERS =====
    def _build_list_cache_key(self, request):
        query_string = request.GET.urlencode()
        digest = hashlib.md5(query_string.encode()).hexdigest()
        return f'listing:list:{digest}'

    def _invalidate_listing_cache(self, listing_id=None):
        invalidate_listing_cache(listing_id)

    # ===== CRUD ACTIONS (Có tích hợp Cache) =====
    def list(self, request, *args, **kwargs):
        cache_key = self._build_list_cache_key(request)
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        ttl = getattr(settings, 'CACHE_TTL_LISTING_LIST', 60 * 15)  # Mặc định 15 phút nếu chưa config
        cache.set(cache_key, response.data, timeout=ttl)
        return response

    def retrieve(self, request, *args, **kwargs):
        # Tăng view trực tiếp ở database bằng F expression chống race-condition
        instance = self.get_object()
        Listing.objects.filter(id=instance.id).update(views_count=F('views_count') + 1)
        instance.refresh_from_db(fields=['views_count'])

        cache_key = f'listing:detail:{instance.id}'
        cached = cache.get(cache_key)
        if cached is not None:
            cached['views_count'] = instance.views_count
            return Response(cached)

        serializer = self.get_serializer(instance)
        data = serializer.data
        ttl = getattr(settings, 'CACHE_TTL_LISTING_DETAIL', 60 * 60)  # Mặc định 1 giờ nếu chưa config
        cache.set(cache_key, data, timeout=ttl)
        return Response(data)

    def perform_create(self, serializer):
        listing = serializer.save(seller=self.request.user)
        images = self.request.FILES.getlist('images')
        for i, image_file in enumerate(images):
            ListingImage.objects.create(
                listing=listing,
                image=image_file,
                is_primary=(i == 0),
            )
        self._invalidate_listing_cache()

    def perform_update(self, serializer):
        listing = serializer.save()
        self._invalidate_listing_cache(listing.id)

    def perform_destroy(self, instance):
        listing_id = instance.id
        instance.delete()
        self._invalidate_listing_cache(listing_id)

    # ===== ACTION DÀNH RIÊNG CHO ADMIN =====
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def approve(self, request, pk=None):
        listing = self.get_object()
        listing.approval_status = Listing.ApprovalStatus.APPROVED
        listing.rejection_reason = None
        listing.reviewed_at = timezone.now()
        listing.reviewed_by = request.user
        listing.save()
        self._invalidate_listing_cache(listing.id)
        return Response({"detail": "Đã duyệt bài đăng."})

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def rejected(self, request):
        queryset = Listing.objects.filter(approval_status=Listing.ApprovalStatus.REJECTED).order_by('-reviewed_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def reject(self, request, pk=None):
        listing = self.get_object()
        listing.approval_status = Listing.ApprovalStatus.REJECTED
        listing.rejection_reason = request.data.get('reason', '')
        listing.reviewed_at = timezone.now()
        listing.reviewed_by = request.user
        listing.save()
        self._invalidate_listing_cache(listing.id)
        return Response({"detail": "Đã từ chối bài đăng."})

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def pending(self, request):
        qs = Listing.objects.filter(approval_status=Listing.ApprovalStatus.PENDING)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    # ===== ACTION DÀNH CHO SELLER =====
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_listings(self, request):
        qs = Listing.objects.filter(seller=request.user)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def upload_images(self, request, pk=None):
        listing = self.get_object()
        if listing.seller != request.user and not request.user.is_staff:
            return Response({"detail": "Không có quyền."}, status=403)

        images = request.FILES.getlist('images')
        if not images:
            return Response({"detail": "Không có ảnh nào được gửi lên."}, status=400)

        has_primary = listing.images.filter(is_primary=True).exists()
        for i, image_file in enumerate(images):
            ListingImage.objects.create(
                listing=listing,
                image=image_file,
                is_primary=(not has_primary and i == 0),
            )
        serializer = self.get_serializer(listing)
        self._invalidate_listing_cache(listing.id)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'], url_path='images/(?P<image_id>[^/.]+)',
            permission_classes=[permissions.IsAuthenticated])
    def delete_image(self, request, pk=None, image_id=None):
        listing = self.get_object()
        if listing.seller != request.user and not request.user.is_staff:
            return Response({"detail": "Không có quyền."}, status=403)

        try:
            image = listing.images.get(id=image_id)
            was_primary = image.is_primary
            image.delete()
            if was_primary:
                next_image = listing.images.first()
                if next_image:
                    next_image.is_primary = True
                    next_image.save(update_fields=['is_primary'])
        except ListingImage.DoesNotExist:
            return Response({"detail": "Không tìm thấy ảnh."}, status=404)

        self._invalidate_listing_cache(listing.id)
        return Response({"detail": "Đã xoá ảnh."})