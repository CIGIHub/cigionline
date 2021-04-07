from core.helpers import CIGIModelAdminPermissionHelper
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks

from .models import PersonPage


@hooks.register('register_permissions')
def register_person_page_permissions():
    person_content_type = ContentType.objects.get(app_label='people', model='personpage')
    return Permission.objects.filter(content_type=person_content_type)


class PersonPageModelAdmin(ModelAdmin):
    model = PersonPage
    menu_label = 'Staff/Experts'
    menu_icon = 'group'
    menu_order = 105
    list_display = ('title', 'position', 'archive', 'live')
    list_filter = ('person_types', 'archive', 'live')
    search_fields = ('title')
    ordering = ['title']
    permission_helper_class = CIGIModelAdminPermissionHelper


modeladmin_register(PersonPageModelAdmin)
