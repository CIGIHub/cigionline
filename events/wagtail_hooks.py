from core.helpers import CIGIModelAdminPermissionHelper
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from wagtail_modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from wagtail import hooks

from .models import EventListPage, EventPage


@hooks.register('register_permissions')
def register_event_list_page_permissions():
    event_list_page_content_type = ContentType.objects.get(app_label='events', model='eventlistpage')
    return Permission.objects.filter(content_type=event_list_page_content_type)


class EventListPageModelAdmin(ModelAdmin):
    model = EventListPage
    menu_label = 'Events Landing Page'
    menu_icon = 'home'
    menu_order = 100
    list_display = ('title',)
    search_fields = ('title',)
    ordering = ['title']
    permission_helper_class = CIGIModelAdminPermissionHelper


@hooks.register('register_permissions')
def register_event_page_permissions():
    event_content_type = ContentType.objects.get(app_label='events', model='eventpage')
    return Permission.objects.filter(content_type=event_content_type)


class EventPageModelAdmin(ModelAdmin):
    model = EventPage
    menu_label = 'Events'
    menu_icon = 'date'
    menu_order = 101
    list_display = ('title', 'publishing_date', 'event_type', 'live')
    list_filter = ('publishing_date', 'event_type', 'live')
    search_fields = ('title',)
    ordering = ['-publishing_date']
    permission_helper_class = CIGIModelAdminPermissionHelper

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(publishing_date__isnull=False)


class EventModelAdminGroup(ModelAdminGroup):
    menu_label = 'Events'
    menu_icon = 'date'
    menu_order = 104
    items = (EventListPageModelAdmin, EventPageModelAdmin)


modeladmin_register(EventModelAdminGroup)
