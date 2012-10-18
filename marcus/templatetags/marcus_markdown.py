import markdown2

from django import template
from django.conf import settings

register = template.Library()


@register.filter(is_safe=True)
def markdown(value):
    return markdown2.markdown(value, extras=settings.MARCUS_MARKDOWN_EXTRAS)
