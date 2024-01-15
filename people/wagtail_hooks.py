from core.helpers import CIGIModelAdminPermissionHelper
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from wagtail import hooks

from .models import PersonListPage, PersonPage


@hooks.register('register_permissions')
def register_person_list_page_permissions():
    person_list_page_content_type = ContentType.objects.get(app_label='people', model='personlistpage')
    return Permission.objects.filter(content_type=person_list_page_content_type)


class PersonListPageModelAdmin(ModelAdmin):
    model = PersonListPage
    menu_label = 'Staff/Expert Landing Pages'
    menu_icon = 'home'
    menu_order = 100
    list_display = ('title',)
    search_fields = ('title',)
    ordering = ['title']
    permission_helper_class = CIGIModelAdminPermissionHelper


@hooks.register('register_permissions')
def register_person_page_permissions():
    person_content_type = ContentType.objects.get(app_label='people', model='personpage')
    return Permission.objects.filter(content_type=person_content_type)


class PersonPageModelAdmin(ModelAdmin):
    model = PersonPage
    menu_label = 'Staff/Experts'
    menu_icon = 'group'
    menu_order = 101
    list_display = ('title', 'position', 'archive', 'live')
    list_filter = ('person_types', 'archive', 'live')
    search_fields = ('title',)
    ordering = ['title']
    permission_helper_class = CIGIModelAdminPermissionHelper


class PersonModelAdminGroup(ModelAdminGroup):
    menu_label = 'Staff/Experts'
    menu_icon = 'group'
    menu_order = 105
    items = (PersonListPageModelAdmin, PersonPageModelAdmin)


modeladmin_register(PersonModelAdminGroup)
