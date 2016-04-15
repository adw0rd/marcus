from django.contrib.sitemaps import GenericSitemap
from django.contrib.flatpages.sitemaps import FlatPageSitemap

from marcus import models


sitemaps = {
    'flatpages': FlatPageSitemap,
    'articles': GenericSitemap(
        {
            'queryset': models.Article.public.language(None).order_by('-published'),
            'date_field': 'published',
        },
        priority=0.9),
    'articles-en': GenericSitemap(
        {
            'queryset': models.Article.public.language('en').order_by('-published'),
            'date_field': 'published',
        },
        priority=0.9),
}
