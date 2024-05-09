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
    ProjectPage,
    ResearchLandingPage,
    TopicPage,
    ThemePage,
)


@hooks.register('register_permissions')
def register_project_page_permissions():
    project_content_type = ContentType.objects.get(app_label='research', model='projectpage')
    return Permission.objects.filter(content_type=project_content_type)


class ProjectPageModelAdmin(ModelAdmin):
    model = ProjectPage
    menu_label = 'Projects'
    menu_icon = 'folder'
    menu_order = 101
    list_display = ('title', 'publishing_date', 'live')
    list_filter = ('publishing_date', 'live')
    search_fields = ('title',)
    ordering = ['-publishing_date']
    permission_helper_class = CIGIModelAdminPermissionHelper

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(publishing_date__isnull=False)


@hooks.register('register_permissions')
def register_research_landing_page_permissions():
    research_landing_content_type = ContentType.objects.get(app_label='research', model='researchlandingpage')
    return Permission.objects.filter(content_type=research_landing_content_type)


class ResearchLandingPageModelAdmin(ModelAdmin):
    model = ResearchLandingPage
    menu_label = 'Research Landing Page'
    menu_icon = 'home'
    menu_order = 100
    list_display = ('title',)
    search_fields = ('title',)
    ordering = ['title']
    permission_helper_class = CIGIModelAdminPermissionHelper


@hooks.register('register_permissions')
def register_topic_page_permissions():
    topic_content_type = ContentType.objects.get(app_label='research', model='topicpage')
    return Permission.objects.filter(content_type=topic_content_type)


class TopicPageModelAdmin(ModelAdmin):
    model = TopicPage
    menu_label = 'Topics'
    menu_icon = 'thumbtack'
    menu_order = 102
    list_display = ('title',)
    list_filter = ('live',)
    search_fields = ('title',)
    ordering = ['title']
    permission_helper_class = CIGIModelAdminPermissionHelper


@hooks.register('register_permissions')
def register_theme_page_permissions():
    theme_content_type = ContentType.objects.get(app_label='research', model='themepage')
    return Permission.objects.filter(content_type=theme_content_type)


class ThemePageModelAdmin(ModelAdmin):
    model = ThemePage
    menu_label = 'Themes'
    menu_icon = 'tag'
    menu_order = 103
    list_display = ('title',)
    search_fields = ('title',)
    ordering = ['title']
    permission_helper_class = CIGIModelAdminPermissionHelper


class ResearchModelAdminGroup(ModelAdminGroup):
    menu_label = 'Research'
    menu_icon = 'site'
    menu_order = 106
    items = (ResearchLandingPageModelAdmin, ThemePageModelAdmin, TopicPageModelAdmin, ProjectPageModelAdmin)


modeladmin_register(ResearchModelAdminGroup)
