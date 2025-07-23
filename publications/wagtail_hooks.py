from wagtail import hooks

from .models import (
    PublicationListPage,
    PublicationPage,
    PublicationSeriesPage,
    PublicationSeriesListPage
)
from wagtail.admin.viewsets.pages import PageListingViewSet
from wagtail.admin.viewsets.base import ViewSetGroup
from wagtail.admin.ui.tables import Column
from utils.admin_utils import title_with_actions, live_icon


class PublicationListPageListingViewSet(PageListingViewSet):
    model = PublicationListPage
    menu_label = 'Publications Landing Page'
    menu_icon = 'home'
    menu_order = 100
    name = 'publicationlistpage'
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    search_fields = ('title',)
    ordering = ['title']


class PublicationsPageListingViewSet(PageListingViewSet):
    model = PublicationPage
    menu_label = 'Publications'
    menu_icon = 'doc-full'
    menu_order = 103
    name = 'publicationpage'
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
        Column('publishing_date', label='Publishing Date', sort_key='publishing_date'),
        Column('publication_type', label='Publication Type', sort_key='publication_type'),
        Column(live_icon, label='Live', sort_key='live'),
        Column('publication_series', label='Publication Series', sort_key='publication_series'),
        Column('id', label='ID', sort_key='id'),
    ]
    list_filter = ('publishing_date', 'publication_type', 'live', 'publication_series')
    search_fields = ('title',)
    ordering = ['-publishing_date']

    def get_index_view_kwargs(self):
        kwargs = super().get_index_view_kwargs()
        kwargs["queryset"] = self.model.objects.filter(publishing_date__isnull=False)
        return kwargs


class PublicationSeriesPageListingViewSet(PageListingViewSet):
    model = PublicationSeriesPage
    menu_label = 'Publication Series'
    menu_icon = 'list-ul'
    menu_order = 104
    name = 'publicationseriespage'
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
        Column('publishing_date', label='Publishing Date', sort_key='publishing_date'),
        Column(live_icon, label='Live', sort_key='live'),
        Column('id', label='ID', sort_key='id'),
    ]
    list_filter = ('publishing_date', 'live')
    search_fields = ('title',)
    ordering = ['-publishing_date']


class PublicationSeriesLandingPageListingViewSet(PageListingViewSet):
    model = PublicationSeriesListPage
    menu_label = 'Publication Series Landing Page'
    menu_icon = 'home'
    menu_order = 101
    name = 'publicationserieslistpage'
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    search_fields = ('title',)
    ordering = ['title']


class PublicationViewSetGroup(ViewSetGroup):
    menu_label = 'Publications'
    menu_icon = 'doc-full'
    menu_order = 103
    items = (PublicationListPageListingViewSet, PublicationsPageListingViewSet, PublicationSeriesPageListingViewSet, PublicationSeriesLandingPageListingViewSet)


@hooks.register('register_admin_viewset')
def register_publication_viewset():
    return PublicationViewSetGroup()
