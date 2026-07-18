from rest_framework import permissions


class IsSellerOrReadOnly(permissions.BasePermission):
    """
    Ai cũng xem được (GET), nhưng chỉ chủ tin đăng mới được sửa/xoá.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.seller == request.user