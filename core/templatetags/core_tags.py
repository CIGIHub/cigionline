from django import template
register = template.Library()


@register.filter
def no_protocol(value):
    return value.replace('http://', '').replace('https://', '')

@register.simple_tag
def define(value=None):
    return value
