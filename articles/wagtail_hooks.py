import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from .models import (
    ArticleLandingPage,
    ArticlePage,
    ArticleSeriesPage,
    MediaLandingPage,
    OpinionSeriesPage,
)
from .rich_text import AnchorEntityElementHandler, anchor_entity_decorator
from utils.admin_utils import title_with_actions, live_icon
from wagtail.admin.viewsets.pages import PageListingViewSet
from wagtail.admin.viewsets.base import ViewSetGroup
from wagtail.admin.ui.tables import Column
from wagtail.admin.rich_text.converters.html_to_contentstate import BlockElementHandler
from wagtail import hooks


@hooks.register('register_rich_text_features')
def register_rich_text_end_of_article(features):
    feature_name = 'endofarticle'
    type_ = 'ENDOFARTICLE'

    control = {
        'type': type_,
        'icon': 'pick',
        'description': 'End of Article',
        'element': 'div',
        'style': {
            'background-color': 'black',
            'height': '25px',
            'margin': '10px auto',
            'width': '25px',
        }
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.BlockFeature(
            control,
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'div[class=end-of-article]': BlockElementHandler(type_)},
        'to_database_format': {'block_map': {type_: {'element': 'div', 'props': {'class': 'end-of-article'}}}},
    })


@hooks.register('register_rich_text_features')
def register_rich_text_anchor(features):
    """
    Registering the `anchor` feature, which uses the `ANCHOR` Draft.js entity type,
    and is stored as HTML with a `<a data-anchor href="#my-anchor">` tag.
    """
    feature_name = 'anchor'
    type_ = 'ANCHOR'

    control = {
        'type': type_,
        'label': '#',
        'description': 'Anchor',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.EntityFeature(
            control,
            js=['admin/js/anchor.js'],
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        # Note here that the conversion is more complicated than for blocks and inline styles.
        'from_database_format': {'a[name]': AnchorEntityElementHandler(type_)},
        'to_database_format': {'entity_decorators': {type_: anchor_entity_decorator}},
    })


class ArticleLandingPageListingViewSet(PageListingViewSet):
    model = ArticleLandingPage
    menu_label = 'Opinions Landing Page'
    icon = 'home'
    menu_order = 100
    name = 'articlelandingpage'
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]


class ArticleSeriesPageListingViewSet(PageListingViewSet):
    model = ArticleSeriesPage
    menu_label = 'Essay Series'
    menu_icon = 'list-ul'
    menu_order = 103
    name = 'articleseriespage'
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
        Column('publishing_date', label='Publishing Date', sort_key='publishing_date'),
        Column('theme', label='Theme', sort_key='theme'),
        Column(live_icon, label='Live', sort_key='live'),
        Column('id', label='ID', sort_key='id'),
    ]
    list_filter = ('publishing_date', 'live')
    search_fields = ('title',)
    ordering = ['-publishing_date']


class MediaLandingPageListingViewSet(PageListingViewSet):
    model = MediaLandingPage
    menu_label = 'Media Landing Page'
    menu_icon = 'home'
    menu_order = 101
    name = 'medialandingpage'
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    search_fields = ('title',)
    ordering = ['title']


class OpinionSeriesPageListingViewSet(PageListingViewSet):
    model = OpinionSeriesPage
    menu_label = 'Opinion Series'
    menu_icon = 'list-ul'
    menu_order = 104
    name = 'opinionseriespage'
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
        Column('publishing_date', label='Publishing Date', sort_key='publishing_date'),
        Column(live_icon, label='Live', sort_key='live'),
        Column('id', label='ID', sort_key='id'),
    ]
    list_filter = ('publishing_date', 'live')
    search_fields = ('title',)
    ordering = ['-publishing_date']


class ArticlePageListingViewSet(PageListingViewSet):
    model = ArticlePage
    menu_label = 'Articles'
    menu_icon = 'copy'
    menu_order = 102
    name = 'articlepage'
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
        Column('publishing_date', label='Publishing Date', sort_key='publishing_date'),
        Column('article_series', label='Article Series', sort_key='article_series'),
        Column('article_type', label='Article Type', sort_key='article_type'),
        Column('theme', label='Theme', sort_key='theme'),
        Column(live_icon, label='Live', sort_key='live'),
        Column('id', label='ID', sort_key='id'),
    ]
    list_filter = ['publishing_date', 'article_type', 'theme', 'live']
    search_fields = ('title',)
    ordering = ['-publishing_date']

    def get_index_view_kwargs(self):
        kwargs = super().get_index_view_kwargs()
        kwargs["queryset"] = self.model.objects.filter(publishing_date__isnull=False)
        return kwargs


class ArticleViewSetGroup(ViewSetGroup):
    menu_label = 'Articles'
    menu_icon = 'copy'
    menu_order = 101
    items = (ArticleLandingPageListingViewSet, MediaLandingPageListingViewSet, ArticlePageListingViewSet, ArticleSeriesPageListingViewSet, OpinionSeriesPageListingViewSet)


@hooks.register("register_admin_viewset")
def register_article_viewset():
    return ArticleViewSetGroup()
