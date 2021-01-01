import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail.core import hooks

from .rich_text import AnchorEntityElementHandler, anchor_entity_decorator


@hooks.register('register_rich_text_features')
def register_rich_text_features(features):
    features.default_features.append('anchor')
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
            js=['admin/anchor.js'],
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        # Note here that the conversion is more complicated than for blocks and inline styles.
        'from_database_format': {'a[data-anchor]': AnchorEntityElementHandler(type_)},
        'to_database_format': {'entity_decorators': {type_: anchor_entity_decorator}},
    })
