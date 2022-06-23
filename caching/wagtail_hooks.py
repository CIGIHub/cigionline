from django.urls import path, reverse
from wagtail.core import hooks
from wagtail.admin.menu import MenuItem
from .urls import urlpatterns


# @hooks.register('register_admin_menu_item')
# def register_caching_menu_item():
#     return MenuItem('Caching', reverse('caching'), icon_name='date')


@hooks.register('register_admin_urls')
def register_admin_urls():
    return urlpatterns
