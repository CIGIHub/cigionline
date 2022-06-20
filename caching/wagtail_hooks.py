from django.urls import path, reverse
from wagtail.core import hooks
from wagtail.admin.menu import MenuItem

from .views import index


@hooks.register('register_admin_urls')
def register_caching_url():
    return [
        path('caching/', index, name='caching'),
    ]


@hooks.register('register_admin_menu_item')
def register_caching_menu_item():
    return MenuItem('Caching', reverse('caching'), icon_name='date')
