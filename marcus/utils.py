# coding: utf-8
import re

from django.contrib.sites.models import Site


def absolute_url(url):
    if url is None or url.startswith('http://') or url.startswith('https://'):
        return url
    return 'http://%s%s' % (Site.objects.get_current().domain, url)


def iurl(url, language):
    return url if not language else '%s%s/' % (url, language)


def altlanguage(language):
    return {'en': None, 'ru': 'en', None: 'en'}.get(language, language)


def get_language_code_in_text(text):
    """Depending of the used language in the text determines the language,
    currently does not include text quotation.

    @return "en" or "ru"
    """
    language = None
    if text:
        language = "ru" if re.search(u'[а-яА-Я]+', text) else "en"
    return language
