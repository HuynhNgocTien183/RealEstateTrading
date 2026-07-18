from django.contrib import admin
from .models import Listing, ListingImage


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'price', 'area', 'property_type', 'status', 'created_at')
    list_filter = ('property_type', 'status', 'city')
    search_fields = ('title', 'address')
    inlines = [ListingImageInline]