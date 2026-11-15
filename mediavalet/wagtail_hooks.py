import json

from django.conf import settings
from django.urls import path, reverse, reverse_lazy
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from . import views


class MediaValetMenuItem(MenuItem):
    def is_shown(self, request):
        return views._can_import(request.user)


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        path("mediavalet/", views.asset_picker_view, name="mediavalet_asset_picker"),
        path(
            "mediavalet/import/",
            views.import_asset_view,
            name="mediavalet_import_asset",
        ),
        path(
            "mediavalet/image-data/<int:image_id>/",
            views.image_data_view,
            name="mediavalet_image_data",
        ),
    ]


@hooks.register("register_admin_menu_item")
def register_mediavalet_menu_item():
    return MediaValetMenuItem(
        label="MediaValet",
        url=reverse_lazy("mediavalet_asset_picker"),
        icon_name="image",
        order=305,
    )


@hooks.register("insert_global_admin_js")
def register_mediavalet_chooser_js():
    config = {
        "importUrl": reverse("mediavalet_import_asset"),
        "imageDataUrl": reverse("mediavalet_image_data", args=[0]).replace(
            "/0/", "/"
        ),
        "pickerUrl": views.get_asset_picker_url(),
    }
    config_json = mark_safe(json.dumps(config).replace("<", "\\u003c"))
    script_url = f'{settings.STATIC_URL.rstrip("/")}/mediavalet/js/image-chooser.js'
    return format_html(
        '<script>window.MEDIAVALET_CONFIG = {};</script>'
        '<script src="{}" defer></script>',
        config_json,
        script_url,
    )
