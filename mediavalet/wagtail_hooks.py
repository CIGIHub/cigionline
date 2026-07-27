import json

from django.templatetags.static import static
from django.urls import path, reverse, reverse_lazy
from django.utils.safestring import mark_safe
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from . import views


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path('mediavalet/', views.asset_picker_view, name='mediavalet_asset_picker'),
        path('mediavalet/import/', views.import_asset_view, name='mediavalet_import_asset'),
        path('mediavalet/image-data/<int:image_id>/', views.image_data_view, name='mediavalet_image_data'),
    ]


@hooks.register('register_admin_menu_item')
def register_mediavalet_menu_item():
    return MenuItem(
        label='MediaValet',
        url=reverse_lazy('mediavalet_asset_picker'),
        icon_name='image',
        order=305,
    )


@hooks.register('insert_editor_js')
def register_mediavalet_chooser_js():
    """
    Injects a config object and the image-chooser script into every Wagtail
    admin editor page, enabling MediaValetImageChooserPanel buttons to work.
    """
    config = {
        'importUrl':    reverse('mediavalet_import_asset'),
        # Strip the trailing placeholder so JS can append the real ID
        'imageDataUrl': reverse('mediavalet_image_data', args=[0]).replace('/0/', '/'),
        'pickerUrl':    views.get_asset_picker_url(),
    }
    return mark_safe(
        f'<script>window.MEDIAVALET_CONFIG = {json.dumps(config)};</script>'
        f'<script src="{static("mediavalet/js/image-chooser.js")}" defer></script>'
    )
