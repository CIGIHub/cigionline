from django import template
register = template.Library()


@register.filter
def clean_phone_number(value):
    return value.replace('.', ' ').lower();
