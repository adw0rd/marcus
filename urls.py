# coding: utf-8
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('marcus.urls')),
    url(r'^', include('subhub.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^sitemap', include('marcus.sitemap_urls')),
)

urlpatterns += staticfiles_urlpatterns()
