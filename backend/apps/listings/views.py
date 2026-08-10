from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone

from .models import Listing
from .serializers import ListingSerializer, ListingCreateSerializer
from .permissions import IsSellerOrReadOnly, IsAdminUser


class ListingViewSet(viewsets.ModelViewSet):
    """
    API quản lý tin đăng bất động sản.

    Quy tắc hiển thị:
    - Khách / chưa đăng nhập: chỉ thấy bài đã được admin duyệt (approved) và đang bán (available)
    - Seller đã đăng nhập: thấy bài approved của người khác + TẤT CẢ bài của chính mình
      (kể cả đang pending/rejected, để tự theo dõi trạng thái)
    - Admin (is_staff=True): thấy toàn bộ, không giới hạn

    Quy tắc chỉnh sửa:
    - Ai cũng xem được (GET) theo phạm vi ở trên
    - Chỉ chủ tin đăng hoặc admin mới được sửa/xoá
    - Chỉ admin mới được duyệt (approve) / từ chối (reject) bài đăng
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsSellerOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property_type', 'city', 'district', 'status', 'bedrooms']
    search_fields = ['title', 'description', 'address']
    ordering_fields = ['price', 'area', 'created_at']

    # ===== QUERYSET theo quyền hạn =====
    def get_queryset(self):
        user = self.request.user

        # Admin thấy toàn bộ
        if user.is_authenticated and user.is_staff:
            return Listing.objects.all()

        # Seller/buyer đã đăng nhập: thấy bài approved + bài của chính mình
        if user.is_authenticated:
            return Listing.objects.filter(
                Q(approval_status=Listing.ApprovalStatus.APPROVED) | Q(seller=user)
            )

        # Khách chưa đăng nhập: chỉ thấy bài đã duyệt và đang bán
        return Listing.objects.filter(
            approval_status=Listing.ApprovalStatus.APPROVED,
            status=Listing.Status.AVAILABLE,
        )

    # ===== SERIALIZER theo action =====
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ListingCreateSerializer
        return ListingSerializer

    # ===== Tạo tin đăng: tự gán seller, mặc định pending (đã xử lý ở model) =====
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    # ===== Xem chi tiết: tự tăng lượt xem =====
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        return super().retrieve(request, *args, **kwargs)

    # ===== ACTION DÀNH RIÊNG CHO ADMIN =====

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def approve(self, request, pk=None):
        """Admin duyệt 1 tin đăng: POST /api/listings/{id}/approve/"""
        listing = self.get_object()
        listing.approval_status = Listing.ApprovalStatus.APPROVED
        listing.rejection_reason = None
        listing.reviewed_at = timezone.now()
        listing.reviewed_by = request.user
        listing.save()
        return Response({"detail": "Đã duyệt bài đăng."})

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def rejected(self, request):
        queryset = Listing.objects.filter(approval_status='rejected').order_by('-reviewed_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def reject(self, request, pk=None):
        """Admin từ chối 1 tin đăng: POST /api/listings/{id}/reject/  Body: {"reason": "..."}"""
        listing = self.get_object()
        listing.approval_status = Listing.ApprovalStatus.REJECTED
        listing.rejection_reason = request.data.get('reason', '')
        listing.reviewed_at = timezone.now()
        listing.reviewed_by = request.user
        listing.save()
        return Response({"detail": "Đã từ chối bài đăng."})

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def pending(self, request):
        """Danh sách bài đang chờ duyệt: GET /api/listings/pending/"""
        qs = Listing.objects.filter(approval_status=Listing.ApprovalStatus.PENDING)
        page = self.paginate_queryset(qs)
        serializer = ListingSerializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    # ===== ACTION DÀNH CHO SELLER =====

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_listings(self, request):
        """Seller xem toàn bộ tin đăng của chính mình (mọi trạng thái): GET /api/listings/my_listings/"""
        qs = Listing.objects.filter(seller=request.user)
        page = self.paginate_queryset(qs)
        serializer = ListingSerializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)