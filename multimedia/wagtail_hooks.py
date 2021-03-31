from .models import MultimediaPage, MultimediaSeriesPage, MultimediaListPage
from wagtail.contrib.modeladmin.options import (ModelAdmin, ModelAdminGroup, modeladmin_register)


class MultimediaListPageAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = MultimediaListPage
    menu_label = 'Multimedia Landing Page'
    menu_icon = 'media'
    menu_order = 100
    list_display = ('title',)


class MultimediaPageAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = MultimediaPage
    menu_label = 'Multimedia'
    menu_icon = 'media'
    menu_order = 101
    list_display = ('title', 'publishing_date', 'multimedia_type', 'multimedia_series', 'theme', 'live')
    list_filter = ('publishing_date', 'multimedia_type', 'multimedia_series', 'theme', 'live')
    search_fields = ('title', 'multimedia_type', 'multimedia_series',)
    ordering = ['-publishing_date']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(publishing_date__isnull=False)


class MultimediaSeriesPageAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = MultimediaSeriesPage
    menu_label = 'Multimedia Series'
    menu_icon = 'media'
    menu_order = 102
    list_display = ('title', 'publishing_date', 'live')
    list_filter = ('publishing_date', 'live')
    search_fields = ('title',)
    ordering = ['-publishing_date']


class MultimediaGroup(ModelAdminGroup):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    menu_label = 'Multimedia'
    menu_icon = 'media'
    menu_order = 102
    items = (MultimediaListPageAdmin, MultimediaPageAdmin, MultimediaSeriesPageAdmin)


modeladmin_register(MultimediaGroup)
