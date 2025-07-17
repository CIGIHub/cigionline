from wagtail import hooks
from .models import AnnualReportListPage, AnnualReportPage
from utils.admin_utils import title_with_actions, live_icon
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.admin.viewsets.base import ViewSetGroup
from wagtail.admin.ui.tables import Column


class AnnualReportListPageListingViewSet(ModelViewSet):
    model = AnnualReportListPage
    menu_label = 'Annual Reports Landing Page'
    menu_icon = 'home'
    menu_order = 100
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    form_fields = ['title',]
    search_fields = ('title',)
    ordering = ['title']


class AnnualReportPageListingViewSet(ModelViewSet):
    model = AnnualReportPage
    menu_label = 'Annual Reports'
    menu_icon = 'history'
    menu_order = 101
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
        Column('year', label='Year', sort_key='year'),
        Column(live_icon, label='Live', sort_key='live'),
        Column('id', label='ID', sort_key='id'),
    ]
    list_filter = ('year', 'live')
    form_fields = ['title', 'year']
    search_fields = ('title',)
    ordering = ['-year']


class AnnualReportViewSetGroup(ViewSetGroup):
    menu_label = 'Annual Reports'
    menu_icon = 'history'
    menu_order = 201
    items = (AnnualReportListPageListingViewSet, AnnualReportPageListingViewSet)


@hooks.register('register_admin_viewset')
def register_annual_report_viewset():
    return AnnualReportViewSetGroup()
