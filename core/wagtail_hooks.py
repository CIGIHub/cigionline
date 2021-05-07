from django.utils.html import format_html
from django.templatetags.static import static
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    BlockElementHandler,
    InlineStyleElementHandler,
)
import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail.core import hooks


@hooks.register('insert_global_admin_css')
def global_admin_css():
    return format_html('<link rel="stylesheet" href="{}">', static('css/admin.css'))


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
        'draftail', feature_name, draftail_features.InlineStyleFeature(
            control,
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'h2[class=paragraph-heading]': InlineStyleElementHandler(type_)},
        'to_database_format': {'style_map': {type_: {'element': 'h2', 'props': {'class': 'paragraph-heading'}}}},
    })
