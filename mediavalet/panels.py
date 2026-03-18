from django.utils.html import format_html
from django.utils.safestring import mark_safe
from wagtail.admin.panels import FieldPanel


class MediaValetImageChooserPanel(FieldPanel):
    """
    A drop-in replacement for FieldPanel on image fields that adds a
    "Choose from MediaValet" button alongside the standard Wagtail image
    chooser.  Usage::

        panels = [
            MediaValetImageChooserPanel('hero_image'),
        ]
    """

    class BoundPanel(FieldPanel.BoundPanel):
        def render_html(self, parent_context=None):
            original_html = str(super().render_html(parent_context))
            if not self.bound_field:
                return mark_safe(original_html)
            # auto_id respects form prefixes (e.g. InlinePanel)
            input_id = self.bound_field.auto_id
            button_html = format_html(
                '<button type="button" '
                '        class="button button--secondary mediavalet-choose-btn" '
                '        data-mediavalet-input-id="{}" '
                '        style="margin-top:-0.5rem;margin-bottom:2rem;">'
                '<svg class="icon icon-image" aria-hidden="true" focusable="false" '
                '     style="width:1em;height:1em;vertical-align:middle;margin-right:0.4em;">'
                '<use href="#icon-image"></use>'
                '</svg>'
                'Choose from MediaValet'
                '</button>',
                input_id,
            )
            return mark_safe(original_html + str(button_html))
