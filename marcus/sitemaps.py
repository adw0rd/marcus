# coding: utf-8
from django.contrib.sitemaps import FlatPageSitemap, GenericSitemap

from marcus import models


sitemaps = {
    'flatpages': FlatPageSitemap,
    'articles': GenericSitemap(
        {
            'queryset': models.Article.objects.exclude(published=None).order_by('-published'),
            'date_field': 'published',
        },
        priority=0.9),
}
