from django.core.cache import cache


def invalidate_listing_cache(listing_id=None):
    if listing_id:
        cache.delete(f'listing:detail:{listing_id}')
    cache.delete_pattern('listing:list:*')