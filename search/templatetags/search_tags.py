from django import template
from wagtail.core.models import Page

register = template.Library()


@register.simple_tag
def live_page_count():
    return Page.objects.live().count()
