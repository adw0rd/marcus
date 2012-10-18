import django.contrib.sitemaps.views as sitemap_views
from django.views.decorators.cache import cache_page
from django.conf.urls import patterns, url

from marcus.sitemaps import sitemaps


urlpatterns = patterns(
    '',
    url(
        r'^\.xml$',
        cache_page(3600)(sitemap_views.index),
        {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps'}),
    url(
        r'^-(?P<section>.+)\.xml$',
        cache_page(3600)(sitemap_views.sitemap),
        {'sitemaps': sitemaps},
        name='sitemaps'),
)
