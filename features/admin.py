from .models import (
    HomePageFeaturedPromotionsList,
    HomePageFeaturedContentList,
    HomePageFeaturedPublicationsList,
    HomePageFeaturedExpertsList,
    HomePageFeaturedMultimediaList,
    HomePageFeaturedHighlightsList,
    HomePageFeaturedEventsList,
)
from wagtail import hooks
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.admin.viewsets.base import ViewSetGroup
from wagtail.admin.ui.tables import Column
from utils.admin_utils import title_with_actions


class HomePageFeaturedContentListViewSet(ModelViewSet):
    model = HomePageFeaturedContentList
    menu_label = 'Home Page Featured Content'
    menu_icon = 'doc-empty'
    menu_order = 201
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    form_fields = ['title']
    search_fields = ('title',)
    ordering = ['title']


class HomePageFeaturedPublicationsListViewSet(ModelViewSet):
    model = HomePageFeaturedPublicationsList
    menu_label = 'Home Page Featured Publications'
    menu_icon = 'doc-full'
    menu_order = 202
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    form_fields = ['title']
    search_fields = ('title',)
    ordering = ['title']


class HomePageFeaturedHighlightsListViewSet(ModelViewSet):
    model = HomePageFeaturedHighlightsList
    menu_label = 'Home Page Featured Highlights'
    menu_icon = 'doc-empty-inverse'
    menu_order = 203
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    form_fields = ['title']
    search_fields = ('title',)
    ordering = ['title']


class HomePageFeaturedMultimediaListViewSet(ModelViewSet):
    model = HomePageFeaturedMultimediaList
    menu_label = 'Home Page Featured Multimedia'
    menu_icon = 'media'
    menu_order = 204
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    form_fields = ['title']
    search_fields = ('title',)
    ordering = ['title']


class HomePageFeaturedExpertsListViewSet(ModelViewSet):
    model = HomePageFeaturedExpertsList
    menu_label = 'Home Page Featured Experts'
    menu_icon = 'group'
    menu_order = 205
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    form_fields = ['title']
    search_fields = ('title',)
    ordering = ['title']


class HomePageFeaturedEventsListViewSet(ModelViewSet):
    model = HomePageFeaturedEventsList
    menu_label = 'Home Page Featured Events'
    menu_icon = 'date'
    menu_order = 206
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    form_fields = ['title']
    search_fields = ('title',)
    ordering = ['title']


class HomePageFeaturedPromotionsListViewSet(ModelViewSet):
    model = HomePageFeaturedPromotionsList
    menu_label = 'Home Page Featured Promotions'
    menu_icon = 'image'
    menu_order = 207
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    form_fields = ['title']
    search_fields = ('title',)
    ordering = ['title']


class FeaturesViewSetGroup(ViewSetGroup):
    menu_label = 'Features'
    menu_icon = 'folder-open-inverse'
    menu_order = 200
    items = (
        HomePageFeaturedContentListViewSet,
        HomePageFeaturedPublicationsListViewSet,
        HomePageFeaturedHighlightsListViewSet,
        HomePageFeaturedMultimediaListViewSet,
        HomePageFeaturedExpertsListViewSet,
        HomePageFeaturedEventsListViewSet,
        HomePageFeaturedPromotionsListViewSet,
    )


@hooks.register('register_admin_viewset')
def register_features_viewset():
    return FeaturesViewSetGroup()
