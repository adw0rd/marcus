import django.contrib.sitemaps.views as sitemap_views
from django.views.decorators.cache import cache_page
from django.urls import path, re_path

from marcus.sitemaps import sitemaps


urlpatterns = [
    path(
        '\.xml',
        cache_page(3600)(sitemap_views.index),
        {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps'}),
    re_path(
        '-(?P<section>.+)\.xml',
        cache_page(3600)(sitemap_views.sitemap),
        {'sitemaps': sitemaps},
        name='sitemaps'),
]
