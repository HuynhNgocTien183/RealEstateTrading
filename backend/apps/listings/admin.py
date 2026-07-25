from django.contrib import admin
from django.utils import timezone
from .models import Listing, ListingImage


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'price', 'area', 'property_type', 'approval_status', 'status', 'created_at')
    list_filter = ('approval_status', 'property_type', 'status', 'city')
    search_fields = ('title', 'address')
    inlines = [ListingImageInline]
    actions = ['approve_listings', 'reject_listings']

    @admin.action(description="Duyệt các bài đăng đã chọn")
    def approve_listings(self, request, queryset):
        queryset.update(
            approval_status=Listing.ApprovalStatus.APPROVED,
            reviewed_at=timezone.now(),
            reviewed_by=request.user,
        )

    @admin.action(description="Từ chối các bài đăng đã chọn")
    def reject_listings(self, request, queryset):
        queryset.update(
            approval_status=Listing.ApprovalStatus.REJECTED,
            reviewed_at=timezone.now(),
            reviewed_by=request.user,
        )