# coding: utf-8
import markdown2
from django import template

register = template.Library()


@register.filter(is_safe=True)
def markdown(value):
    return markdown2.markdown(value)
