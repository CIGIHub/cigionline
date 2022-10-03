from core.helpers import CIGIModelAdminPermissionHelper
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from wagtail import hooks

from .models import (
    MultimediaListPage,
    MultimediaPage,
    MultimediaSeriesPage,
)


@hooks.register('register_permissions')
def register_multimedia_list_page_permissions():
    multimedia_list_page_content_type = ContentType.objects.get(app_label='multimedia', model='multimedialistpage')
    return Permission.objects.filter(content_type=multimedia_list_page_content_type)


class MultimediaListPageModelAdmin(ModelAdmin):
    model = MultimediaListPage
    menu_label = 'Multimedia Landing Page'
    menu_icon = 'home'
    menu_order = 100
    list_display = ('title',)
    search_fields = ('title',)
    ordering = ['title']
    permission_helper_class = CIGIModelAdminPermissionHelper


@hooks.register('register_permissions')
def register_multimedia_page_permissions():
    multimedia_content_type = ContentType.objects.get(app_label='multimedia', model='multimediapage')
    return Permission.objects.filter(content_type=multimedia_content_type)


class MultimediaPageModelAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = MultimediaPage
    menu_label = 'Multimedia'
    menu_icon = 'media'
    menu_order = 101
    list_display = ('title', 'publishing_date', 'multimedia_type', 'multimedia_series', 'theme', 'live')
    list_filter = ('publishing_date', 'multimedia_type', 'multimedia_series', 'theme', 'live')
    search_fields = ('title',)
    ordering = ['-publishing_date']
    permission_helper_class = CIGIModelAdminPermissionHelper

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(publishing_date__isnull=False)


class MultimediaSeriesPageModelAdmin(ModelAdmin):
    model = MultimediaSeriesPage
    menu_label = 'Multimedia Series'
    menu_icon = 'list-ul'
    menu_order = 102
    list_display = ('title', 'publishing_date', 'live')
    list_filter = ('publishing_date', 'live')
    search_fields = ('title',)
    ordering = ['-publishing_date']
    permission_helper_class = CIGIModelAdminPermissionHelper

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(publishing_date__isnull=False)


class MultimediaModelAdminGroup(ModelAdminGroup):
    menu_label = 'Multimedia'
    menu_icon = 'media'
    menu_order = 102
    items = (MultimediaListPageModelAdmin, MultimediaPageModelAdmin, MultimediaSeriesPageModelAdmin)


modeladmin_register(MultimediaModelAdminGroup)
