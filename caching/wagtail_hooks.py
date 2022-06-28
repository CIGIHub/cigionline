from django.urls import path, reverse
from wagtail.core import hooks
from wagtail.admin.menu import MenuItem, SubmenuMenuItem
from wagtail.contrib.modeladmin.menus import SubMenu
from .urls import urlpatterns


@hooks.register('register_admin_urls')
def register_admin_urls():
    return urlpatterns


@hooks.register("register_admin_menu_item")
def register_caching_menu_item():
    menu_items = [
        MenuItem('Articles', reverse('caching:caching_articles'), icon_name='doc-full'),
        MenuItem('Article Series', reverse('caching:caching_article_series'), icon_name='doc-full'),
    ]

    return SubmenuMenuItem('Caching', SubMenu(menu_items), icon_name="bin", order=700)
