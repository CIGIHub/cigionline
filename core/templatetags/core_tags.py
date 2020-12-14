from django import template
import datetime
from pytz import timezone, utc
register = template.Library()


@register.filter
def no_protocol(value):
    return value.replace('http://', '').replace('https://', '')


@register.filter
def page_type(page):
    return page._meta.verbose_name.lower().replace(' ', '-')


@register.filter
def in_list(value, the_list):
    return value in the_list.split(',')


@register.simple_tag
def define(value):
    return value


@register.filter
def social_string(value):
    return value.replace(' ', '+')
