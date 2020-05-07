from django import template
register = template.Library()


@register.filter
def trim(value):
    return value.strip()
    

@register.filter
def no_protocol(value):
    return value.replace('http://', '').replace('https://', '')
