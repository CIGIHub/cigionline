from django import template
register = template.Library()

@register.simple_tag
def define(val=None):
  return val

@register.filter
def no_protocol(value):
    return value.replace('http://', '').replace('https://', '')
