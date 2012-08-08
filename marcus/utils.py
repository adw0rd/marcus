# -*- coding:utf-8 -*-
from django.contrib.sites.models import Site

def absolute_url(url):
    if url is None or url.startswith('http://') or url.startswith('https://'):
        return url
    return 'http://%s%s' % (Site.objects.get_current().domain, url)

def iurl(url, language):
    return url if not language else '%s%s/' % (url, language)

def altlanguage(language):
    return {'en': None, 'ru': 'en', None: 'en'}.get(language, language)
