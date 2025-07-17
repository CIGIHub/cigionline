from wagtail import hooks
from .models import (
    ProjectPage,
    ResearchLandingPage,
    TopicPage,
    ThemePage,
    CountryPage,
)
from utils.admin_utils import title_with_actions, live_icon
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.admin.viewsets.base import ViewSetGroup
from wagtail.admin.ui.tables import Column


class ResearchLandingPageListingViewSet(ModelViewSet):
    model = ResearchLandingPage
    menu_label = 'Research Landing Page'
    menu_icon = 'home'
    menu_order = 100
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    form_fields = ['title',]
    search_fields = ('title',)
    ordering = ['title']


class ThemePageListingViewSet(ModelViewSet):
    model = ThemePage
    menu_label = 'Themes'
    menu_icon = 'tag'
    menu_order = 103
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    form_fields = ['title',]
    search_fields = ('title',)
    ordering = ['title']


class TopicPageListingViewSet(ModelViewSet):
    model = TopicPage
    menu_label = 'Topics'
    menu_icon = 'thumbtack'
    menu_order = 102
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    form_fields = ['title',]
    search_fields = ('title',)
    ordering = ['title']


class ProjectPageListingViewSet(ModelViewSet):
    model = ProjectPage
    menu_label = 'Projects'
    menu_icon = 'folder'
    menu_order = 101
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
        Column('publishing_date', label='Publishing Date', sort_key='publishing_date'),
        Column(live_icon, label='Live', sort_key='live'),
        Column('id', label='ID', sort_key='id'),
    ]
    list_filter = ('publishing_date', 'live')
    form_fields = ['title', 'publishing_date']
    search_fields = ('title',)
    ordering = ['-publishing_date']


class CountryPageListingViewSet(ModelViewSet):
    model = CountryPage
    menu_label = 'Countries'
    menu_icon = 'site'
    menu_order = 104
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    form_fields = ['title',]
    search_fields = ('title',)
    ordering = ['title']


class ResearchViewSetGroup(ViewSetGroup):
    menu_label = 'Research'
    menu_icon = 'site'
    menu_order = 106
    items = (
        ResearchLandingPageListingViewSet,
        ThemePageListingViewSet,
        TopicPageListingViewSet,
        ProjectPageListingViewSet,
        CountryPageListingViewSet,
    )


@hooks.register('register_admin_viewset')
def register_research_viewsets():
    return ResearchViewSetGroup()
