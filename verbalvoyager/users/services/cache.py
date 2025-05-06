import datetime as dt

from django.core.cache import cache
from django.views.decorators.cache import cache_page

def user_cache(view_func):
    def _wrapped_view(request, *args, **kwargs):
        CACHE_KEY_PREFIX = f"user_{request.user.id}_{request.path}"
        return cache_page(
            60 * 15,
            key_prefix=CACHE_KEY_PREFIX
        )(view_func)(request, *args, **kwargs)
    return _wrapped_view

def session_cache(view_func):
    def _wrapped_view(request, *args, **kwargs):
        CACHE_KEY_PREFIX = f"user_{request.session.session_key}_{request.path}"
        return cache_page(
            60 * 15,
            key_prefix=CACHE_KEY_PREFIX
        )(view_func)(request, *args, **kwargs)
    return _wrapped_view