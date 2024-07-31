from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    BlockElementHandler,
    InlineStyleElementHandler,
)
from wagtail_modeladmin.options import (ModelAdmin, modeladmin_register)
import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail import hooks
from wagtail.models import Page
from .models import Theme


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


class ThemeModelAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = Theme
    menu_label = 'Themes'
    menu_icon = 'image'
    menu_order = 204
    list_display = ('name',)
    search_fields = ('name',)


# sort page chooser panels by most recent pages
@hooks.register('construct_page_chooser_queryset')
def order_pages_in_chooser(pages, request):
    if "choose-page" in request.path:
        return pages.order_by('-live', '-latest_revision_created_at')
    return pages


class AboutModelAdmin(ModelAdmin):
    model = Page
    menu_label = 'About'
    menu_icon = 'help'
    menu_order = 110
    list_display = ('title',)
    search_fields = ('title',)

    page_names = [
        'CIGI History',
        'Our Partners',
        'CIGI Campus',
        'Strategy and Evaluation',
        'The CIGI Rule',
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(title__in=self.page_names)


modeladmin_register(ThemeModelAdmin)
modeladmin_register(AboutModelAdmin)
