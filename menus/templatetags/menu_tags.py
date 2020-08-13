from django import template

from ..models import Menu

register = template.Library()


@register.simple_tag()
def get_menu_items(slug):
    return Menu.objects.get(slug=slug).menu_items.all
