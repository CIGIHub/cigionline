from core.helpers import CIGIModelAdminPermissionHelper
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from wagtail import hooks

from .models import AnnualReportListPage, AnnualReportPage


@hooks.register('register_permissions')
def register_annual_report_list_page_permissions():
    annual_report_list_page_content_type = ContentType.objects.get(app_label='annual_reports', model='annualreportlistpage')
    return Permission.objects.filter(content_type=annual_report_list_page_content_type)


class AnnualReportListPageModelAdmin(ModelAdmin):
    model = AnnualReportListPage
    menu_label = 'Annual Reports Landing Page'
    menu_icon = 'home'
    menu_order = 100
    list_display = ('title',)
    search_fields = ('title',)
    ordering = ['title']
    permission_helper_class = CIGIModelAdminPermissionHelper


@hooks.register('register_permissions')
def register_annual_report_page_permissions():
    annual_report_page_content_type = ContentType.objects.get(app_label='annual_reports', model='annualreportpage')
    return Permission.objects.filter(content_type=annual_report_page_content_type)


class AnnualReportPageModelAdmin(ModelAdmin):
    model = AnnualReportPage
    menu_label = 'Annual Reports'
    menu_icon = 'history'
    list_display = ('title',)
    list_filter = ('live',)
    search_fields = ('title',)
    ordering = ['-title']
    permission_helper_class = CIGIModelAdminPermissionHelper


class AnnualReportModelAdminGroup(ModelAdminGroup):
    menu_label = 'Annual Reports'
    menu_icon = 'history'
    menu_order = 201
    items = (AnnualReportListPageModelAdmin, AnnualReportPageModelAdmin)


modeladmin_register(AnnualReportModelAdminGroup)
