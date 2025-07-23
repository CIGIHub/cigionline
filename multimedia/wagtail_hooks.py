from wagtail import hooks
from wagtail.admin.ui.tables import Column
from utils.admin_utils import title_with_actions, live_icon
from .models import (
    MultimediaListPage,
    MultimediaPage,
    MultimediaSeriesPage,
)
from wagtail.admin.viewsets.pages import PageListingViewSet
from wagtail.admin.viewsets.base import ViewSetGroup


class MultimediaPageListingViewSet(PageListingViewSet):
    model = MultimediaPage
    menu_label = 'Multimedia'
    menu_icon = 'media'
    menu_order = 102
    name = 'multimediapage'
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
        Column('publishing_date', label='Publishing Date', sort_key='publishing_date'),
        Column('multimedia_type', label='Multimedia Type', sort_key='article_type'),
        Column('article_series', label='Article Series', sort_key='article_series'),
        Column('multimedia_series', label='Multimedia Series', sort_key='multimedia_series'),
        Column('theme', label='Theme', sort_key='theme'),
        Column(live_icon, label='Live', sort_key='live'),
    ]
    list_filter = ['publishing_date', 'multimedia_type', 'article_series', 'multimedia_series', 'theme', 'live']
    search_fields = ('title',)
    ordering = ['-publishing_date']


class MultimediaLandingPageListingViewSet(PageListingViewSet):
    model = MultimediaListPage
    menu_label = 'Multimedia Landing Page'
    menu_icon = 'home'
    menu_order = 100
    name = 'multimedialistpage'
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    search_fields = ('title',)
    ordering = ['title']


class MultimediaSeriesPageListingViewSet(PageListingViewSet):
    model = MultimediaSeriesPage
    menu_label = 'Multimedia Series'
    menu_icon = 'list-ul'
    menu_order = 103
    name = 'multimediaseriespage'
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
        Column('publishing_date', label='Publishing Date', sort_key='publishing_date'),
        Column(live_icon, label='Live', sort_key='live'),
        Column('id', label='ID', sort_key='id'),
    ]
    list_filter = ('publishing_date', 'live')
    search_fields = ('title',)
    ordering = ['-publishing_date']


class MultimediaViewSetGroup(ViewSetGroup):
    menu_label = 'Multimedia'
    menu_icon = 'media'
    menu_order = 102
    items = (MultimediaLandingPageListingViewSet, MultimediaPageListingViewSet, MultimediaSeriesPageListingViewSet)


@hooks.register("register_admin_viewset")
def register_multimedia_viewset():
    return MultimediaViewSetGroup()
