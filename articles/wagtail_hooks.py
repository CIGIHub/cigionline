from wagtail.admin.rich_text.converters.html_to_contentstate import BlockElementHandler
import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail.core import hooks
from articles.models import ArticlePage
from wagtail.contrib.modeladmin.options import (ModelAdmin, modeladmin_register)

from .rich_text import AnchorEntityElementHandler, anchor_entity_decorator


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
