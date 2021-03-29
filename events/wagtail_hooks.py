from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from wagtail.contrib.modeladmin.helpers import PagePermissionHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks

from .models import EventPage


@hooks.register('register_permissions')
def register_event_page_permissions():
    event_content_type = ContentType.objects.get(app_label='events', model='eventpage')
    return Permission.objects.filter(content_type=event_content_type)


class EventPageModelAdminPermissionHelper(PagePermissionHelper):
    def user_can_list(self, user):
        return self.user_has_any_permissions(user)


class EventPageModelAdmin(ModelAdmin):
    model = EventPage
    menu_label = 'Events'
    menu_icon = 'date'
    menu_order = 104
    list_display = ('title', 'publishing_date', 'event_type', 'live')
    list_filter = ('publishing_date', 'event_type', 'live')
    search_fields = ('title')
    ordering = ['-publishing_date']
    permission_helper_class = EventPageModelAdminPermissionHelper

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(publishing_date__isnull=False)


modeladmin_register(EventPageModelAdmin)
