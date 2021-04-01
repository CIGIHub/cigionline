from .models import AnnualReportPage, AnnualReportListPage
from wagtail.contrib.modeladmin.options import (ModelAdmin, modeladmin_register, ModelAdminGroup)


class AnnualReportListPageAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = AnnualReportListPage
    menu_label = 'AnnualReport Landing Page'
    menu_icon = 'date'
    menu_order = 100
    list_display = ('title',)


class AnnualReportPageAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = AnnualReportPage
    menu_label = 'AnnualReports'
    menu_icon = 'date'
    menu_order = 101
    list_display = ('title', 'year', 'live')
    list_filter = ('year', 'live')
    search_fields = ('title', 'year',)
    ordering = ['-year']


class AnnualReportGroup(ModelAdminGroup):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    menu_label = 'AnnualReports'
    menu_icon = 'date'
    menu_order = 120
    items = (AnnualReportListPageAdmin, AnnualReportPageAdmin)


modeladmin_register(AnnualReportGroup)
