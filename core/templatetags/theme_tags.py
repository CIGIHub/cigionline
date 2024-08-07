from datetime import datetime
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def dph_term(value):
    date = datetime.strptime(value, '%Y-%m-%d %H:%M:%S%z')

    year = date.year
    month = date.month

    if (month <= 4):
        term = 'Fall'
        year = year - 1
    elif 5 <= month <= 8:
        term = 'Winter'
    elif 9 <= month <= 12:
        term = 'Summer'
    else:
        term = ''

    return f'{term} {year} term'
