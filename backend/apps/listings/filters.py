import django_filters
from .models import Listing


class ListingFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Listing
        fields = ['property_type', 'district', 'status', 'bedrooms']