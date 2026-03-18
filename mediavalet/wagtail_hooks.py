from django.urls import path, reverse_lazy
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from . import views


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path('mediavalet/', views.asset_picker_view, name='mediavalet_asset_picker'),
        path('mediavalet/import/', views.import_asset_view, name='mediavalet_import_asset'),
    ]


@hooks.register('register_admin_menu_item')
def register_mediavalet_menu_item():
    return MenuItem(
        label='MediaValet',
        url=reverse_lazy('mediavalet_asset_picker'),
        icon_name='image',
        order=305,
    )
