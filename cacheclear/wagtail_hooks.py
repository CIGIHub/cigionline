from django.urls import path, reverse
from wagtail.core import hooks
from wagtail.admin.menu import MenuItem

from .views import index


@hooks.register('register_admin_urls')
def register_cacheclear_url():
    return [
        path('cacheclear/', index, name='cacheclear'),
    ]


@hooks.register('register_admin_menu_item')
def register_cacheclear_menu_item():
    return MenuItem('Cache Clear', reverse('cacheclear'), icon_name='date')