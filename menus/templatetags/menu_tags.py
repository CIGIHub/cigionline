from django import template

from ..models import Menu

register = template.Library()


@register.simple_tag()
def get_menu_items(slug):
    return Menu.objects.prefetch_related(
        'menu_items__link_page',
        'menu_items__submenu__menu_items__link_page',
    ).get(slug=slug).menu_items.all()


@register.filter
def menu_icon(menu_item):
    icons = {
        'Research': 'fa-file-alt',
        'Publications': 'fa-book',
        'Experts': 'fa-user',
        'Opinions': 'fa-comment-alt-lines',
        'Multimedia': 'fa-film',
        'Events': 'fa-calendar',
        'About': 'fa-university',
    }
    return icons[menu_item]
