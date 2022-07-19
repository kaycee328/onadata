"""
Cache control mixin
"""
from typing import Optional

from django.conf import settings
from django.utils.cache import patch_cache_control


class CacheControlBase:
    """
    Base class for Cache Control header handlers
    """
    CACHE_CONTROL_DIRECTIVES = {"max_age": 60}

    def set_cache_control(self, response, cache_control_directives: Optional[dict] = None):
        """
        Sets the `Cache-Control` headers on a `Response`
        Object
        """
        cache_control_directives = self.CACHE_CONTROL_DIRECTIVES
        if hasattr(settings, 'CACHE_CONTROL_DIRECTIVES'):
            cache_control_directives = settings.CACHE_CONTROL_DIRECTIVES

        patch_cache_control(response, **cache_control_directives)
        return response


class CacheControlMiddleware(CacheControlBase):
    """
    Django Middleware used to set `Cache-Control` header for every response
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return self.set_cache_control(response)


class CacheControlMixin(CacheControlBase):
    """
    Django Rest Framework ViewSet mixin for Cache-Control
    """
    def finalize_response(self, request, response, *args, **kwargs):
        if (
            request.method == "GET"
            and not response.streaming
            and response.status_code in [200, 201, 202]
        ):
            response = self.set_cache_control(response)

        return super().finalize_response(
            request, response, *args, **kwargs
        )
