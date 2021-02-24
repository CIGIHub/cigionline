from django import template

from ..models import Menu

register = template.Library()


@register.simple_tag()
def get_menu_items(slug):
    return Menu.objects.prefetch_related(
        'menu_items__link_page',
        'menu_items__submenu__menu_items__link_page',
    ).get(slug=slug).menu_items.all()
