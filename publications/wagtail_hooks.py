from publications.models import PublicationPage, PublicationSeriesPage, PublicationListPage
from wagtail.contrib.modeladmin.options import (ModelAdmin, ModelAdminGroup, modeladmin_register)


class PublicationListPageAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = PublicationListPage
    menu_label = 'Publication Landing Page'
    menu_icon = 'doc-full'
    menu_order = 100
    list_display = ('title',)


class PublicationPageAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = PublicationPage
    menu_label = 'Publications'
    menu_icon = 'doc-full'
    menu_order = 101
    list_display = ('title', 'publishing_date', 'publication_type', 'live', 'publication_series')
    list_filter = ('publishing_date', 'publication_type', 'live', 'publication_series')
    search_fields = ('title')
    ordering = ['-publishing_date']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(publishing_date__isnull=False)


class PublicationSeriesPageAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = PublicationSeriesPage
    menu_label = 'Publication Series'
    menu_icon = 'doc-full'
    menu_order = 102
    list_display = ('title', 'publishing_date', 'live',)
    list_filter = ('publishing_date', 'live',)
    search_fields = ('title')
    ordering = ['-publishing_date']


class PublicationsGroup(ModelAdminGroup):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    menu_label = 'Publications'
    menu_icon = 'doc-full'
    menu_order = 103
    items = (PublicationListPageAdmin, PublicationPageAdmin, PublicationSeriesPageAdmin)


modeladmin_register(PublicationsGroup)
