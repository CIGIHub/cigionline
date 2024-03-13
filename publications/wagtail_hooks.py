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
    PublicationListPage,
    PublicationPage,
    PublicationSeriesPage,
    PublicationSeriesListPage
)


@hooks.register('register_permissions')
def register_publication_list_page_permissions():
    publication_list_page_content_type = ContentType.objects.get(app_label='publications', model='publicationlistpage')
    return Permission.objects.filter(content_type=publication_list_page_content_type)


class PublicationListPageModelAdmin(ModelAdmin):
    model = PublicationListPage
    menu_label = 'Publications Landing Page'
    menu_icon = 'home'
    menu_order = 100
    list_display = ('title',)
    search_fields = ('title',)
    ordering = ['title']
    permission_helper_class = CIGIModelAdminPermissionHelper


class PublicationSeriesListPageModelAdmin(ModelAdmin):
    model = PublicationSeriesListPage
    menu_label = 'Publications Series Landing Page'
    menu_icon = 'home'
    menu_order = 200
    list_display = ('title',)
    search_fields = ('title',)
    ordering = ['title']
    permission_helper_class = CIGIModelAdminPermissionHelper


@hooks.register('register_permissions')
def register_publication_page_permissions():
    publication_content_type = ContentType.objects.get(app_label='publications', model='publicationpage')
    return Permission.objects.filter(content_type=publication_content_type)


class PublicationPageModelAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = PublicationPage
    menu_label = 'Publications'
    menu_icon = 'doc-full'
    menu_order = 300
    list_display = ('title', 'publishing_date', 'publication_type', 'live', 'publication_series')
    list_filter = ('publishing_date', 'publication_type', 'live', 'publication_series')
    search_fields = ('title',)
    ordering = ['-publishing_date']
    permission_helper_class = CIGIModelAdminPermissionHelper

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(publishing_date__isnull=False)


class PublicationSeriesPageModelAdmin(ModelAdmin):
    model = PublicationSeriesPage
    menu_label = 'Publication Series'
    menu_icon = 'list-ul'
    menu_order = 400
    list_display = ('title', 'publishing_date', 'live')
    list_filter = ('publishing_date', 'live')
    search_fields = ('title',)
    ordering = ['-publishing_date']
    permission_helper_class = CIGIModelAdminPermissionHelper

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(publishing_date__isnull=False)


class PublicationModelAdminGroup(ModelAdminGroup):
    menu_label = 'Publications'
    menu_icon = 'doc-full'
    menu_order = 103
    items = (PublicationListPageModelAdmin, PublicationPageModelAdmin, PublicationSeriesPageModelAdmin, PublicationSeriesListPageModelAdmin)


modeladmin_register(PublicationModelAdminGroup)
