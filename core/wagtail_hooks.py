from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    BlockElementHandler,
    InlineStyleElementHandler,
)
import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail import hooks
from wagtail.models import Page
from .models import Theme
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.admin.ui.tables import Column
from utils.admin_utils import title_with_actions
from wagtail.snippets.views.snippets import SnippetViewSet


@hooks.register('insert_global_admin_css')
def global_admin_css():
    return format_html('<link rel="stylesheet" href="{}">', static('css/admin.css'))


@hooks.register('insert_editor_js')
def editor_js():
    return mark_safe(
        """
        <script>
            /**
            * @param {jQuery} $
            */
            window.addEventListener("DOMContentLoaded", (event) => {
                var times = [];
                for (let i = 0; i < 24; i++) {
                    var hour = i < 10 ? "0" + i : i;
                    times.push(hour + ":" + "00");
                    times.push(hour + ":" + "30");
                }
                $("#id_go_live_at").siblings("script").innerHtml = initDateTimeChooser(
                    "id_go_live_at",
                    {"dayOfWeekStart": 0, "format": "Y-m-d H:i", "formatTime": "H:i", "allowTimes": times}
                );
                $("#id_go_live_at").attr("readonly", "")
            });
        </script>
        """
    )


@hooks.register('register_rich_text_features')
def register_rich_text_drop_cap(features):
    feature_name = 'dropcap'
    type_ = 'DROPCAP'

    control = {
        'type': type_,
        'icon': 'title',
        'description': 'Drop cap',
        'element': 'div',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.BlockFeature(
            control,
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'div[class=drop-caps]': BlockElementHandler(type_)},
        'to_database_format': {'block_map': {type_: {'element': 'div', 'props': {'class': 'drop-caps'}}}},
    })


@hooks.register('register_rich_text_features')
def register_rich_text_name(features):
    feature_name = 'name'
    type_ = 'NAME'

    control = {
        'type': type_,
        'label': 'Name',
        'description': 'Name',
        'element': 'span',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.InlineStyleFeature(
            control,
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'span[class=name]': InlineStyleElementHandler(type_)},
        'to_database_format': {'style_map': {type_: {'element': 'span', 'props': {'class': 'name'}}}},
    })


@hooks.register('register_rich_text_features')
def register_rich_text_coloured(features):
    feature_name = 'coloured'
    type_ = 'COLOURED'

    control = {
        'type': type_,
        'label': 'Coloured',
        'description': 'Coloured',
        'element': 'span',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.InlineStyleFeature(
            control,
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'span[class=coloured]': InlineStyleElementHandler(type_)},
        'to_database_format': {'style_map': {type_: {'element': 'span', 'props': {'class': 'coloured'}}}},
    })


@hooks.register('register_rich_text_features')
def register_rich_text_underline(features):
    feature_name = 'underline'
    type_ = 'UNDERLINE'

    control = {
        'type': type_,
        'label': 'U',
        'description': 'underline',
        'element': 'span',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.InlineStyleFeature(
            control,
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'span[class=underline]': InlineStyleElementHandler(type_)},
        'to_database_format': {'style_map': {type_: {'element': 'span', 'props': {'class': 'underline'}}}},
    })


@hooks.register('register_rich_text_features')
def register_rich_text_paragraph_heading(features):
    feature_name = 'paragraph_heading'
    type_ = 'HEADING'

    control = {
        'type': type_,
        'label': 'Heading',
        'description': 'Paragraph Heading',
        'element': 'h2',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.BlockFeature(
            control,
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'h2[class=paragraph-heading]': BlockElementHandler(type_)},
        'to_database_format': {'block_map': {type_: {'element': 'h2', 'props': {'class': 'paragraph-heading'}}}},
    })


@hooks.register('register_rich_text_features')
def register_rich_text_rtl(features):
    feature_name = 'rtl'
    type_ = 'RTL'

    control = {
        'type': type_,
        'label': 'R',
        'description': 'Right-to-left language support',
        'element': 'p',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.BlockFeature(
            control,
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'p[dir=rtl]': BlockElementHandler(type_)},
        'to_database_format': {'block_map': {type_: {'element': 'p', 'props': {'dir': 'rtl'}}}},
    })


class AboutListingViewSet(ModelViewSet):
    model = Page
    menu_label = 'About'
    menu_icon = 'help'
    menu_order = 110
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    search_fields = ('title',)
    form_fields = ['title']
    page_names = [
        'CIGI History',
        'Our Partners',
        'CIGI Campus',
        'Strategy and Evaluation',
        'The CIGI Rule',
    ]
    add_to_admin_menu = True

    def get_index_view_kwargs(self):
        kwargs = super().get_index_view_kwargs()
        kwargs["queryset"] = self.model.objects.filter(title__in=AboutListingViewSet.page_names)
        return kwargs


class ThemeListingViewSet(SnippetViewSet):
    model = Theme
    menu_label = 'Themes'
    menu_icon = 'image'
    menu_order = 204
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    form_fields = ['name']
    search_fields = ('name',)
    ordering = ['name']
    add_to_admin_menu = True


@hooks.register("register_admin_viewset")
def register_theme_viewset():
    return ThemeListingViewSet()


@hooks.register("register_admin_viewset")
def register_about_viewset():
    return AboutListingViewSet()
