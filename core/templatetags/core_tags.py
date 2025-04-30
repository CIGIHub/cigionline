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


@register.filter
def any_in_list(values, the_list):
    for value in values:
        if str(value) in the_list.split(','):
            return True
    return False


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
        cigi_prefix = 'CIGI ' if 'cigi' not in value.lower() else ''
        return f'Former {cigi_prefix}{value}'
    return value


@register.filter
@stringfilter
def trim_trailing_slash(value):
    if value.endswith('/'):
        return value[:-1]
    return value


@register.filter
@stringfilter
def dash_case(value):
    return value.lower().replace(' ', '-')


@register.filter(name='split_to_spans')
def split_to_spans(value):
    if not isinstance(value, str):
        return value
    return ''.join(f'<span id="char-{i}">{char}</span>' for i, char in enumerate(value))


@register.filter
@stringfilter
def revert_snake_case(value):
    return value.lower().replace('_', ' ')


@register.filter
def remove_trailing_s(value):
    if isinstance(value, str) and value.endswith('s'):
        return value[:-1]
    return value
