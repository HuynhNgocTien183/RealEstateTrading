from rest_framework import permissions


class IsSellerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.seller == request.user or request.user.is_staff


class IsAdminUser(permissions.BasePermission):
    """Chỉ admin (is_staff=True) mới được duyệt bài."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff