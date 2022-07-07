from core.helpers import CIGIModelAdminPermissionHelper
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from wagtail import hooks

from .models import JobPostingListPage, JobPostingPage


@hooks.register('register_permissions')
def register_job_posting_list_page_permissions():
    job_posting_list_page_content_type = ContentType.objects.get(app_label='careers', model='jobpostinglistpage')
    return Permission.objects.filter(content_type=job_posting_list_page_content_type)


class JobPostingListPageModelAdmin(ModelAdmin):
    model = JobPostingListPage
    menu_label = 'Careers Page'
    menu_icon = 'home'
    menu_order = 100
    list_display = ('title',)
    search_fields = ('title',)
    ordering = ['title']
    permission_helper_class = CIGIModelAdminPermissionHelper


@hooks.register('register_permissions')
def register_job_posting_page_permissions():
    job_posting_page_content_type = ContentType.objects.get(app_label='careers', model='jobpostingpage')
    return Permission.objects.filter(content_type=job_posting_page_content_type)


class JobPostingPageModelAdmin(ModelAdmin):
    model = JobPostingPage
    menu_label = 'Job Postings'
    menu_icon = 'user'
    list_display = ('title', 'live')
    list_filter = ('live',)
    search_fields = ('title',)
    ordering = ['-live', 'title']
    permission_helper_class = CIGIModelAdminPermissionHelper


class JobPostingModelAdminGroup(ModelAdminGroup):
    menu_label = 'Careers'
    menu_icon = 'user'
    menu_order = 202
    items = (JobPostingListPageModelAdmin, JobPostingPageModelAdmin)


modeladmin_register(JobPostingModelAdminGroup)
