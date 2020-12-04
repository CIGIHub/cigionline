from django import template
register = template.Library()


@register.filter
def no_protocol(value):
    return value.replace('http://', '').replace('https://', '')


@register.filter
def social_string(value):
    return value.replace(' ', '+')

  