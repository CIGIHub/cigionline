from .models import ProjectPage, TopicPage, ResearchLandingPage
from wagtail.contrib.modeladmin.options import (ModelAdmin, ModelAdminGroup, modeladmin_register)


class ResearchLandingPageAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = ResearchLandingPage
    menu_label = 'Research Landing Page'
    menu_icon = 'form'
    menu_order = 100
    list_display = ('title',)


class ProjectPageAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = ProjectPage
    menu_label = 'Projects'
    menu_icon = 'form'
    menu_order = 101
    list_display = ('title', 'publishing_date', 'project_types', 'live')
    list_filter = ('publishing_date', 'project_types', 'live')
    search_fields = ('title', 'project_types',)
    ordering = ['-publishing_date']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(publishing_date__isnull=False)


class TopicPageAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = TopicPage
    menu_label = 'Topics'
    menu_icon = 'snippet'
    menu_order = 102
    list_display = ('title', 'live')
    list_filter = ('live')
    search_fields = ('title',)
    ordering = ['title']


class ResearchGroup(ModelAdminGroup):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    menu_label = 'Research'
    menu_icon = 'form'
    menu_order = 104
    items = (ResearchLandingPageAdmin, ProjectPageAdmin, TopicPageAdmin)


modeladmin_register(ResearchGroup)
