from datetime import datetime
from pathlib import Path

from django import template

from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
def no_protocol(value):
    return value.replace('http://', '').replace('https://', '')


@register.filter
def page_type(page):
    if page and hasattr(page, '_meta'):
        return page._meta.verbose_name.lower().replace(' ', '-')
    return ''


@register.filter
def in_list(value, the_list):
    return value in the_list.split(',')


@register.simple_tag
def define(value):
    return value


@register.filter
def social_string(value):
    return value.replace(' ', '+')


@register.filter
def file_extension(value):
    return Path(value).suffix


@register.simple_tag(takes_context=True)
def preview_cache_bust(context):
    if context['request']:
        if hasattr(context['request'], 'is_preview'):
            if context['request'].is_preview:
                return datetime.now().strftime("%Y%m%d%H%M%S")
    return ''


@register.filter
@stringfilter
def formerize_position(value):
    if 'former' not in value.lower():
        return f'Former {value}'
    return value
