from datetime import datetime
from pathlib import Path
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from collections import OrderedDict

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


@register.inclusion_tag("streams/persons_tabs.html", takes_context=True)
def render_persons_groups(context, stream_value, block_type_name="persons_list"):
    """
    Collect all PersonsListBlocks (by block_type or label) from a StreamField and group them by 'title'.
    For each block, pre-render its HTML so switching years is instant on the client.
    """
    request = context.get("request")
    groups = OrderedDict()
    order_counter = 0

    for child in getattr(stream_value, "stream_data", []) or stream_value:
        if hasattr(child, "block_type"):
            bt = child.block_type
            value = child.value
            block = child.block
        else:
            bt = child.get("type")
            value = child.get("value")
            block = None

        if bt != block_type_name:
            continue

        title = (value.get("title") or "").strip() or "People"
        year = value.get("year")

        if hasattr(child, "block"):
            html = child.block.render(value, context.flatten())
        else:
            html = ""

        groups.setdefault(title, [])
        groups[title].append({
            "year": year,
            "html": mark_safe(html),
            "key": f"{order_counter}",
        })
        order_counter += 1

    return {
        "groups": groups,
        "request": request,
    }
