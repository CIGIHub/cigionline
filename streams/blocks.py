from bs4 import BeautifulSoup
from django import forms
from django.conf import settings
from django.db import models
from django.forms.utils import flatatt
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.html import format_html, format_html_join, strip_tags
from django.utils.safestring import mark_safe
import wagtail.rich_text as rich_text
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail import blocks
from wagtail.blocks.struct_block import StructBlockAdapter
from wagtail.telepath import register as telepath_register
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtailmedia.blocks import AbstractMediaChooserBlock
import pytz
import uuid
from django.core.exceptions import ValidationError
from django.template import TemplateDoesNotExist
from django.template.loader import get_template, render_to_string


class ConditionalFieldsMixin:
    """Editor-only conditional fields for a StructBlock form: show only the
    fields for the selected option of a controlling child.

    ``CONDITIONAL_FIELDS`` maps a controlling child block to the fields each
    of its values reveals, e.g. ``{'mode': {'auto': ['count'], 'manual':
    ['items']}}``. Any field listed under at least one value is "controlled":
    hidden for values that don't list it. Unlisted fields always show.
    BooleanBlock controllers use ``'true'``/``'false'`` keys.

    Presentation-only (ds_block_conditionals.js): hidden fields still submit
    and keep their values — switching the toggle back loses nothing — and
    render-time logic already ignores the irrelevant fields, so nothing may
    couple validation to visibility. Maps are assigned centrally at the bottom
    of this module.
    """

    CONDITIONAL_FIELDS = {}


class ConditionalStructBlockAdapter(StructBlockAdapter):
    """StructBlock telepath adapter carrying the conditional-fields map to the
    editor (the documented customization path for StructBlock forms)."""

    js_constructor = 'cigionline.blocks.ConditionalStructBlock'

    def js_args(self, block):
        args = super().js_args(block)
        args[-1]['conditionalFields'] = block.CONDITIONAL_FIELDS
        return args

    @cached_property
    def media(self):
        base = super().media
        return forms.Media(
            js=list(base._js) + ['js/admin/ds_block_conditionals.js'],
            css=base._css,
        )


class FacetedListingBlockAdapter(ConditionalStructBlockAdapter):
    """Faceted Listing's editor adapter: the conditional-fields map plus the
    per-card-type facet capability map, so the facet picker offers only the
    groups the chosen card type can build (BugHerd #442). The map is imported
    lazily — core.faceted_listing imports this module."""

    js_constructor = 'cigionline.blocks.FacetedListingStructBlock'

    def js_args(self, block):
        args = super().js_args(block)
        from core.faceted_listing import FACETS_BY_CARD_TYPE
        args[-1]['facetSupport'] = {
            key: list(groups) for key, groups in FACETS_BY_CARD_TYPE.items()}
        return args


telepath_register(ConditionalStructBlockAdapter(), ConditionalFieldsMixin)


def _template_exists(name):
    try:
        get_template(name)
    except TemplateDoesNotExist:
        return False
    return True


class ThemeableBlock:
    implemented_themes = []

    def get_theme_dir(self, theme_name):
        return theme_name.lower().replace(' ', '_').replace("-", '_')

    def get_page_type_dir(self, verbose_name):
        return verbose_name.lower().replace(' ', '_')

    def get_theme_template(self, standard_template, context, template_name):
        if (
            context and
            context.get('page') and
            isinstance(context['page'], Page) and
            context['page'].get_site()
        ):
            site = context['page'].get_site()
            # Only where a Think 7 copy exists (paragraph, persons_list): every
            # other ThemeableBlock on a Think 7 page falls through to its
            # standard template instead of raising TemplateDoesNotExist —
            # including the four blocks that joined this mixin for BugHerd #522.
            if site.site_name == 'Think 7 Canada' and _template_exists(f'think7/streams/{template_name}.html'):
                return f'think7/streams/{template_name}.html'

        if (
            context and
            context.get('page') and
            hasattr(context['page'], '_meta') and
            hasattr(context['page']._meta, 'verbose_name') and
            hasattr(context['page'], 'theme') and
            context['page'].theme and
            f'{self.get_theme_dir(context["page"].theme.name)}_{self.get_page_type_dir(context["page"]._meta.verbose_name)}' in self.implemented_themes
        ):
            return f'themes/{self.get_theme_dir(context["page"].theme.name)}/streams/{self.get_page_type_dir(context["page"]._meta.verbose_name)}_{template_name}.html'

        # A page rendering its pre-redesign theme fork gets the pre-redesign
        # block too: the DS block templates drop the Bootstrap container and
        # lean on the .ds-prose column, which a legacy fork doesn't have
        # (John, BugHerd #522). Blocks with no legacy copy stay DS.
        if (
            context and
            getattr(context.get('page'), 'renders_legacy_fork', False) and
            _template_exists(f'streams/legacy/{template_name}.html')
        ):
            return f'streams/legacy/{template_name}.html'
        return standard_template


class VideoBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        if not value:
            return ''

        player_code = '''
        <div>
            <video width="320" height="240" controls>
                {0}
                Your browser does not support the video tag.
            </video>
        </div>
        '''

        return format_html(player_code, format_html_join(
            '\n', "<source{0}",
            [[flatatt(s)] for s in value.sources]
        ))


class ButtonBlock(blocks.StructBlock):
    """Shared, design-system button. Target resolves page > document > URL.

    Variant + scheme + icon are presentation tokens; styling is driven entirely
    by the design-system SCSS (no per-instance one-off styles).
    """

    class Variant(models.TextChoices):
        OUTLINE = ('outline', 'Outline')
        SOLID = ('solid', 'Solid (accent fill)')
        TERTIARY = ('tertiary', 'Tertiary (text + chevron)')

    class Scheme(models.TextChoices):
        # Auto resolves from the surrounding module's surface at render time
        # (templates pass `button_surface`; see the `button_scheme` tag). An
        # explicitly authored scheme always wins. Default — a button dropped
        # on a red banner mustn't render red-on-red because the author never
        # touched the scheme dropdown.
        AUTO = ('auto', 'Auto (match surface)')
        ON_LIGHT = ('on-light', 'On light surface')
        ON_DARK = ('on-dark', 'On dark / image surface')
        ON_RED = ('on-red', 'On red panel')

    class Icon(models.TextChoices):
        NONE = ('', 'No icon')
        CHEVRON = ('chevron', 'Chevron')
        ARROW = ('arrow', 'Arrow')
        DOWNLOAD = ('download', 'Download')

    label = blocks.CharBlock(required=True)
    link_page = blocks.PageChooserBlock(required=False)
    link_document = DocumentChooserBlock(required=False)
    link_url = blocks.CharBlock(required=False, help_text='External or relative URL. Used only if no page or document is set.')
    variant = blocks.ChoiceBlock(choices=Variant.choices, default=Variant.OUTLINE, max_length=16)
    scheme = blocks.ChoiceBlock(choices=Scheme.choices, default=Scheme.AUTO, max_length=16)
    icon = blocks.ChoiceBlock(choices=Icon.choices, default=Icon.CHEVRON, required=False, max_length=16)

    class Meta:
        icon = 'link'
        label = 'Button'
        template = 'streams/button_block.html'


class AccordionBlock(blocks.StructBlock, ThemeableBlock):
    title = blocks.CharBlock(required=True)
    text = blocks.RichTextBlock(
        features=[
            'bold',
            'h3',
            'h4',
            'italic',
            'link',
            'ol',
            'ul',
        ],
        required=True,
    )
    # Per-item button row, below the item's body (BugHerd #186).
    buttons = blocks.ListBlock(ButtonBlock(), required=False, default=[])


    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(AccordionBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'accordion_block')

    class Meta:
        icon = 'edit'
        label = 'Accordion'
        template = 'streams/accordion_block.html'


class SurfaceMixin(blocks.StructBlock):
    """Shared surface (mode) + accent picker for design-system modules.

    `surface` chooses the background/text treatment; `accent` chooses the
    highlight colour. Both map 1:1 to `.ds-surface--*` modifier classes; all
    colours come from design-system tokens (no per-instance styling).
    """

    class Surface(models.TextChoices):
        INHERIT = ('inherit', 'Inherit from page')
        LIGHT = ('light', 'Light')
        DARK = ('dark', 'Dark')
        CHARCOAL = ('charcoal', 'Charcoal (DPH dark)')
        RED = ('red', 'Red')
        GREEN = ('green', 'Green')
        TEAL = ('teal', 'Teal (Data & Economy)')
        BLUE = ('blue', 'Blue (AI & Tech)')
        OLIVE = ('olive', 'Olive (Security)')
        MAUVE = ('mauve', 'Mauve (Governance)')

    class Accent(models.TextChoices):
        RED = ('red', 'Red')
        GREEN = ('green', 'Green')
        TEAL = ('teal', 'Teal')
        BLUE = ('blue', 'Blue')
        OLIVE = ('olive', 'Olive')
        MAUVE = ('mauve', 'Mauve')

    surface = blocks.ChoiceBlock(choices=Surface.choices, default=Surface.INHERIT, max_length=8)
    accent = blocks.ChoiceBlock(choices=Accent.choices, default=Accent.RED, max_length=8)


class AccordionModuleBlock(blocks.StructBlock, ThemeableBlock):
    """Two-column accordion section: intro (heading + rich text + button row)
    beside a group of accordion items. Reuses the existing AccordionBlock as the
    item shape so legacy `accordion` content migrates cleanly.
    """

    heading = blocks.CharBlock(required=False)
    intro_text = blocks.RichTextBlock(
        features=['bold', 'italic', 'link', 'ol', 'ul'],
        required=False,
    )
    buttons = blocks.ListBlock(ButtonBlock(), required=False, default=[])
    items = blocks.ListBlock(AccordionBlock())
    # Surface/accent like other DS modules (DPH FAQs sit on charcoal,
    # 1595:95008). Defaults inherit — existing placements unchanged.
    surface = blocks.ChoiceBlock(choices=SurfaceMixin.Surface.choices, default=SurfaceMixin.Surface.INHERIT, required=False)
    accent = blocks.ChoiceBlock(choices=SurfaceMixin.Accent.choices, required=False)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        # Unique group name so native <details name> single-open behaviour is
        # scoped to this module (multiple modules on a page don't interfere).
        context['group_id'] = 'ds-accordion-%s' % uuid.uuid4().hex[:8]
        return context

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(AccordionModuleBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'accordion_module_block')

    class Meta:
        icon = 'list-ul'
        label = 'Accordion Module'
        template = 'streams/accordion_module_block.html'


class TextColumnsBlock(blocks.StructBlock, ThemeableBlock):
    """The "Text" module: a heading (+ top-rule) and intro in a left column, and
    a single flowing rich-text body (sub-headings, lists, paragraphs) in a right
    column. Two-up on desktop, stacked on mobile. Distinct from Text Card Grid
    (which is an equal-card grid).
    """

    heading = blocks.CharBlock(required=False)
    intro = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
        help_text='Short intro under the heading (left column).',
    )
    buttons = blocks.ListBlock(ButtonBlock(), required=False, default=[])
    body = blocks.RichTextBlock(
        features=['bold', 'italic', 'link', 'h3', 'h4', 'ol', 'ul'],
        required=False,
        help_text='Main content (right column) — sub-headings, lists, paragraphs.',
    )
    # Surface/accent like other DS modules (DPH Application tab alternates
    # charcoal/green text sections, 1595:95008). Defaults inherit.
    surface = blocks.ChoiceBlock(choices=SurfaceMixin.Surface.choices, default=SurfaceMixin.Surface.INHERIT, required=False)
    accent = blocks.ChoiceBlock(choices=SurfaceMixin.Accent.choices, required=False)
    # Partner-logos variant of the right column: logo + short
    # text per item, divider-separated, with a small ruled footnote spanning
    # underneath. Authors leave `body` empty for the exact frame.
    logos = blocks.ListBlock(
        blocks.StructBlock([
            # Optional, so the chooser's menu offers "Clear choice" — required,
            # editors only got Change/Edit and no way to remove a logo (Tia +
            # Evan, BugHerd #369). A cleared row renders nothing.
            ('logo', ImageChooserBlock(required=False)),
            ('text', blocks.RichTextBlock(
                features=['bold', 'italic', 'link'], required=False)),
        ]),
        required=False,
        default=[],
        help_text='Optional partner-logo row (right column): a logo and short text each. '
                  'Clear a row\'s logo (or delete the row) to remove it from the page.',
    )
    footnote = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
        help_text='Small ruled footnote under the logo row.',
    )

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(TextColumnsBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'text_columns_block')

    class Meta:
        icon = 'doc-full'
        label = 'Text'
        template = 'streams/text_columns_block.html'


class StatBlock(blocks.StructBlock):
    """A single stat: a large number/figure and a short label."""

    number = blocks.CharBlock(required=True, help_text='e.g. "100+", "20", "3+"')
    label = blocks.CharBlock(required=True)

    class Meta:
        icon = 'doc-full'
        label = 'Stat'


class StatsBlock(SurfaceMixin, ThemeableBlock):
    """Section title (heading + intro + buttons) over an N-up row of stats.

    Sits on a coloured surface; the stat underline uses the chosen accent. All
    presentation is driven by surface/accent tokens — no per-instance styles.
    """

    heading = blocks.CharBlock(required=False)
    intro_text = blocks.RichTextBlock(
        features=['bold', 'italic', 'link', 'ol', 'ul'],
        required=False,
    )
    buttons = blocks.ListBlock(ButtonBlock(), required=False, default=[])
    stats = blocks.ListBlock(StatBlock())

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(StatsBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'stats_block')

    class Meta:
        icon = 'list-ul'
        label = 'Stats'
        label_format = '{heading}'  # collapsed/minimap label shows the heading, not the surface (BugHerd #92)
        template = 'streams/stats_block.html'


class ImageTextBlock(blocks.StructBlock, ThemeableBlock):
    """Image beside a content column. The content column distributes top→bottom:
    a heading with the thick (10px) top-rule motif at the top, and a one- or
    two-column body with an optional button row at the bottom.
    """

    class ImagePosition(models.TextChoices):
        LEFT = ('left', 'Image left')
        RIGHT = ('right', 'Image right')

    image = ImageChooserBlock(required=True)
    image_position = blocks.ChoiceBlock(
        choices=ImagePosition.choices,
        default=ImagePosition.LEFT,
        max_length=8,
    )
    heading = blocks.CharBlock(required=False)
    body = blocks.RichTextBlock(
        features=['bold', 'italic', 'link', 'ol', 'ul'],
        required=False,
    )
    body_secondary = blocks.RichTextBlock(
        features=['bold', 'italic', 'link', 'ol', 'ul'],
        required=False,
        help_text='Optional second body column shown beside the first.',
    )
    buttons = blocks.ListBlock(ButtonBlock(), required=False, default=[])

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(ImageTextBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'image_text_block')

    class Meta:
        icon = 'image'
        label = 'Image + Text'
        template = 'streams/image_text_block.html'


class CTAImageBlock(blocks.StructBlock, ThemeableBlock):
    """Full-bleed call to action: a background image with a heading pinned to the
    top and a red panel (rich text + button row) at the bottom. Image is required;
    the panel is always the brand-red surface (per the design).

    NB: named CTAImageBlock (not CTABlock) — a legacy `CTABlock` already exists.
    """

    image = ImageChooserBlock(required=True)
    heading = blocks.CharBlock(required=False)
    text = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
    )
    buttons = blocks.ListBlock(ButtonBlock(), required=False, default=[])

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(CTAImageBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'cta_image_block')

    class Meta:
        icon = 'image'
        label = 'CTA (with image)'
        template = 'streams/cta_image_block.html'


class AltHeroBlock(blocks.StructBlock, ThemeableBlock):
    """Full-bleed hero: background image over a black base with a heavy top/bottom
    gradient. Content is anchored to the bottom — a breadcrumb/eyebrow and large
    title on the left, an optional description on the right. White text throughout.
    """

    image = ImageChooserBlock(required=True)
    eyebrow = blocks.CharBlock(required=False, help_text='Breadcrumb / label above the title. Use ">" to separate crumbs, e.g. "Home > CIGI Experts".')
    heading = blocks.CharBlock(required=False)
    description = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        # Split the eyebrow into breadcrumb parts as plain (unlinked) crumb
        # objects — same shape the page-hero breadcrumbs tag produces, so the
        # shared partial renders both the same way. (Real linked breadcrumbs are
        # page chrome; in a body block the eyebrow is just a label.)
        eyebrow = value.get('eyebrow') or ''
        context['crumbs'] = [
            {'title': part.strip(), 'url': None, 'current': False}
            for part in eyebrow.split('>') if part.strip()
        ]
        return context

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(AltHeroBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'alt_hero_block')

    class Meta:
        icon = 'image'
        label = 'Alt Hero'
        template = 'streams/alt_hero_block.html'


class HeroTabBlock(blocks.StructBlock):
    """A single tab in a Secondary Hero: a label and its content panel."""

    label = blocks.CharBlock(required=True)
    content = blocks.RichTextBlock(
        features=['bold', 'h3', 'h4', 'italic', 'link', 'ol', 'ul'],
        required=True,
    )

    class Meta:
        icon = 'doc-full'
        label = 'Tab'


class SplitHeroBlock(SurfaceMixin, ThemeableBlock):
    """Split hero with no background image: a text column (breadcrumb + title +
    body) beside an image/logo column, divided by a vertical rule, on a coloured
    surface. Surface-aware (text/divider from surface tokens); microsite themes
    supply specific colours.
    """

    eyebrow = blocks.CharBlock(required=False, help_text='Breadcrumb / label above the title. Use ">" to separate crumbs.')
    heading = blocks.CharBlock(required=False)
    description = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
    )
    image = ImageChooserBlock(required=False, help_text='Optional image/logo shown beside the text.')

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        eyebrow = value.get('eyebrow') or ''
        context['crumbs'] = [
            {'title': part.strip(), 'url': None, 'current': False}
            for part in eyebrow.split('>') if part.strip()
        ]
        return context

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(SplitHeroBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'split_hero_block')

    class Meta:
        icon = 'image'
        label = 'Split Hero'
        label_format = '{heading}'  # collapsed/minimap label shows the heading, not the surface (BugHerd #92)
        template = 'streams/split_hero_block.html'


class PrimaryHeroBlock(SurfaceMixin, ThemeableBlock):
    """Primary hero on a solid surface — no image. Large title and an optional
    description, left-aligned and top-anchored. The lead page hero. Surface-aware
    (defaults to the dark CIGI surface).
    """

    heading = blocks.CharBlock(required=False)
    description = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
    )
    # Primary hero is dark by default (solid CIGI black surface).
    surface = blocks.ChoiceBlock(choices=SurfaceMixin.Surface.choices, default=SurfaceMixin.Surface.DARK, max_length=8)

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(PrimaryHeroBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'primary_hero_block')

    class Meta:
        icon = 'image'
        label = 'Primary Hero'
        label_format = '{heading}'  # collapsed/minimap label shows the heading, not the surface (BugHerd #92)
        template = 'streams/primary_hero_block.html'


class HorizontalTabsBlock(blocks.StructBlock, ThemeableBlock):
    """Standalone horizontal tab strip + content panels (no hero). Each tab
    reveals a rich-text panel; WAI-ARIA tablist enhanced by tabs.js (all panels
    visible without JS). Reuses the shared `.ds-tabs` component + HeroTabBlock.
    """

    heading = blocks.CharBlock(required=False, help_text='Optional accessible label for the tab group.')
    tabs = blocks.ListBlock(HeroTabBlock())

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        # Unique id so multiple tab groups on a page don't collide.
        context['group_id'] = 'ds-tabs-%s' % uuid.uuid4().hex[:8]
        return context

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(HorizontalTabsBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'horizontal_tabs_block')

    class Meta:
        icon = 'list-ul'
        label = 'Horizontal Tabs'
        template = 'streams/horizontal_tabs_block.html'


class TextCardBlock(blocks.StructBlock):
    """A single text card: a heading, a body, and an optional button. No image."""

    heading = blocks.CharBlock(required=True)
    text = blocks.RichTextBlock(
        features=['bold', 'italic', 'link', 'ol', 'ul'],
        required=True,
    )
    # Per-card button — the card's text link as a real DS button (BugHerd #185).
    buttons = blocks.ListBlock(ButtonBlock(), required=False, default=[])

    class Meta:
        icon = 'doc-full'
        label = 'Card'


class TextCardGridBlock(SurfaceMixin, ThemeableBlock):
    """Section title (heading + intro) above a grid of text cards separated by
    divider rules. 3 or 4 cards per row; extra cards wrap to further rows (a
    horizontal rule divides the rows). Surface-aware (light by default).
    """

    heading = blocks.CharBlock(required=False)
    intro = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
    )
    columns = blocks.ChoiceBlock(
        choices=[('2', '2 per row'), ('3', '3 per row'), ('4', '4 per row')],
        default='3',
        max_length=1,
    )
    # Author-set button row under the section intro (BugHerd #172).
    buttons = blocks.ListBlock(ButtonBlock(), required=False, default=[])
    cards = blocks.ListBlock(TextCardBlock())

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(TextCardGridBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'text_card_grid_block')

    class Meta:
        icon = 'list-ul'
        label = 'Text Card Grid'
        label_format = '{heading}'  # collapsed/minimap label shows the heading, not the surface (BugHerd #92)
        template = 'streams/text_card_grid_block.html'


class VideoCardBlock(blocks.StructBlock):
    """A single video card: a click-to-load facade (poster + play button) with a
    topic tag, title and description.
    """

    poster_image = ImageChooserBlock(required=True, help_text='Thumbnail shown before the video plays.')
    video_url = blocks.URLBlock(required=False, help_text='YouTube or Vimeo URL.')
    video_file = VideoBlock(required=False, help_text='Uploaded file. Takes precedence over a URL.')
    tag = blocks.CharBlock(required=False, help_text='Topic label shown above the title (e.g. "Trade Digitization").')
    accent = blocks.ChoiceBlock(choices=SurfaceMixin.Accent.choices, default='teal', max_length=8, help_text='Topic accent colour for the tag.')
    title = blocks.CharBlock(required=True)
    description = blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False)

    class Meta:
        icon = 'media'
        label = 'Video card'


class VideoCarouselBlock(ConditionalFieldsMixin, blocks.StructBlock, ThemeableBlock):
    """Section title over a 3-up carousel of video cards — each a click-to-load
    facade (poster + play) with a topic tag, title and description. Reuses the
    shared carousel ([data-ds-carousel]) + video facade. Loop is disabled for
    video carousels (Swiper would clone slides and drop the facade handlers).
    """

    heading = blocks.CharBlock(required=False)
    intro_text = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
    )
    items = blocks.ListBlock(VideoCardBlock())

    # Carousel controls (shared across all DS carousels)
    show_pagination = blocks.BooleanBlock(required=False, default=True, help_text='Show the pagination dots/numbers.')
    loop = blocks.BooleanBlock(required=False, default=True, help_text='Return to the first slide after the last (needs ≥8 slides for the peek to loop).')
    autoplay = blocks.BooleanBlock(required=False, default=False, help_text='Advance slides automatically.')
    autoplay_speed = blocks.IntegerBlock(required=False, default=5, min_value=1, help_text='Seconds between slides when autoplay is on.')

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(VideoCarouselBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'video_carousel_block')

    class Meta:
        icon = 'media'
        label = 'Video Carousel'
        template = 'streams/video_carousel_block.html'


class FormSectionBlock(blocks.StructBlock, ThemeableBlock):
    """Venue Rental form module: module-level heading + intro with the
    facility-rental inquiry form embedded below (fields fixed in code —
    core.forms.FacilityRentalInquiryForm). Rendered multi-step client-side
    (multistep-form.js); posts to the venue_rental_inquiry view, which emails
    EmailFormSettings.recipients. See docs/redesign/forms.md.
    """

    heading = blocks.CharBlock(required=False)
    intro = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
        help_text='Optional description shown above the form.',
    )
    # Left-panel contact rows (Figma 1360:106576): a small heading over
    # icon + text lines. Email/phone rows auto-link.
    contact_heading = blocks.CharBlock(
        required=False,
        help_text='e.g. "For Further Information, Please Contact:"',
    )
    contacts = blocks.ListBlock(
        blocks.StructBlock([
            # Fax joins the set on request (Tia, BugHerd #235). Only email and
            # phone auto-link in the template; a fax number stays plain text.
            ('icon', blocks.ChoiceBlock(
                choices=[('email', 'Email'), ('phone', 'Phone'), ('fax', 'Fax'), ('address', 'Address')],
                default='email')),
            ('text', blocks.CharBlock()),
        ]),
        required=False, default=[],
        help_text='Contact lines under the heading (email and phone become links).',
    )
    # Band behind the section (BugHerd #163, Evan). Light stays the default so
    # the staged venue form keeps its QA-approved white band; the form chrome is
    # surface-aware (_form.scss), so dark and charcoal render legibly.
    surface = blocks.ChoiceBlock(
        choices=[('light', 'Light'), ('dark', 'Dark'), ('charcoal', 'Charcoal (DPH dark)')],
        default='light', max_length=8,
        help_text='Background band behind the form section.',
    )

    # The embedded form — the ONLY thing GeneralInquiryBlock changes (#163).
    # Both render through the same section template and form include.
    form_action_name = 'venue_rental_inquiry'

    def make_form(self):
        from core.forms import FacilityRentalInquiryForm
        return FacilityRentalInquiryForm()

    def get_context(self, value, parent_context=None):
        from django.urls import reverse

        context = super().get_context(value, parent_context)
        # A bound form (from an invalid POST re-render) may already be in
        # context; don't clobber it.
        if not context.get('section_form'):
            context['section_form'] = self.make_form()
        context['section_form_action'] = reverse(self.form_action_name)
        return context

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(FormSectionBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'form_section_block')

    class Meta:
        icon = 'form'
        label = 'Venue Rental Form'
        template = 'streams/form_section_block.html'


class GeneralInquiryBlock(FormSectionBlock):
    """General Inquiries form module (BugHerd #163; wireframe 764:16168): the
    venue module with core.forms.GeneralInquiryForm swapped in — name pair,
    email, message, consent. Aside, surface and contact rows are inherited."""

    form_action_name = 'general_inquiry'

    def make_form(self):
        from core.forms import GeneralInquiryForm
        return GeneralInquiryForm()

    class Meta:
        icon = 'form'
        label = 'General Inquiries Form'
        template = 'streams/form_section_block.html'


class ExpertCardSlotsBlock(blocks.StructBlock):
    """Author toggles for the optional expert-card slots.

    A dynamic module that renders expert cards (Experts Carousel/Grid, etc.)
    nests this so editors choose which slots show. Pass the value straight to the
    card — keys match the tag's args: ``{% expert_card person slots=self.card_slots %}``.
    Avatar + name are always on (not toggleable). Defaults mirror the common grid
    card: role + expertise on, bio + latest-activity off.
    """

    show_title = blocks.BooleanBlock(required=False, default=True, label='Show role / title')
    show_bio = blocks.BooleanBlock(required=False, default=False, label='Show bio')
    show_expertise = blocks.BooleanBlock(required=False, default=True, label='Show expertise tags')
    show_latest_activity = blocks.BooleanBlock(required=False, default=False, label='Show latest activity')
    show_read_bio = blocks.BooleanBlock(required=False, default=False, label='Show "Read Bio" link')

    class Meta:
        icon = 'user'
        label = 'Expert card slots'


def selected_or_auto(chooser_value):
    """Portion-3 selection/visibility helper, reused by every dynamic module that
    exposes an optional ordered page chooser.

    Returns the author's chosen pages — cleaned to live + specific, in chooser
    order — when any were picked, else ``None`` to signal "auto" (the module falls
    back to its default queryset). So an empty chooser = the module's automatic
    behaviour; a populated one = exactly those pages, in that order.
    """
    chosen = [page.specific for page in (chooser_value or [])
              if page and getattr(page, 'live', False)]
    return chosen or None


class SpotlightProgramBlock(blocks.StructBlock):
    """One spotlighted program, with optional hand-picked content cards."""

    program = blocks.PageChooserBlock(page_type='research.ProjectPage')
    content_pages = blocks.ListBlock(
        blocks.PageChooserBlock(),
        required=False,
        label='Cards (optional)',
        help_text='Hand-pick and order up to 2 content cards for this program. '
                  'Leave empty to show its 2 most recent live pages.', default=[],
    )

    class Meta:
        icon = 'site'
        label = 'Program'


class ProgramSpotlightBlock(blocks.StructBlock, ThemeableBlock):
    """Dynamic module: the research taxonomy rendered live. Authors supply the
    section heading + intro and may optionally choose/order the programs to
    spotlight; left empty, the program tablist is queried automatically (all live
    programs, research-theme order, ThemeProgram display labels). The themes row
    (ThemePage, tree order, accent) is always queried at render time; each program's
    cards default to its two latest content pages but can be hand-picked per program.
    """

    heading = blocks.CharBlock(required=False, help_text='Section heading (e.g. "Our Research").')
    intro = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
    )
    themes_eyebrow = blocks.CharBlock(
        required=False, default='Research Themes',
        help_text='Eyebrow above the themes row (rendered uppercase).',
    )
    programs_eyebrow = blocks.CharBlock(
        required=False, default='Research Program Topics',
        help_text='Eyebrow above the programs tablist (rendered uppercase).',
    )
    programs = blocks.ListBlock(
        SpotlightProgramBlock(),
        required=False,
        label='Programs (optional)',
        help_text='Choose and order the programs to spotlight (and optionally their '
                  'cards). Leave empty to show all live programs automatically, in '
                  'research-theme order, each with its 2 most recent pages.', default=[],
    )

    @staticmethod
    def _spotlight_entry(program, theme, title, content_pages=None):
        """One program panel's context (theme, display title, cards).
        Cards show each item's own topic pills, like every other content card — the
        panel already names the program, so a program pill would only repeat it
        (BugHerd #519). When the author hand-picks `content_pages` we honour that
        order (live only, capped at 2); otherwise we query program.content_pages
        (the reverse of ContentPage.projects) for the 2 latest. .specific()
        bulk-fetches concrete types so the card presenter's page.specific is a no-op.
        """
        if content_pages:
            cards = [p.specific for p in content_pages if p and p.live][:2]
        else:
            cards = (program.content_pages.live().public()
                     .order_by('-publishing_date').specific()[:2])
        return {
            'theme': theme,
            'title': title,
            'page': program,
            'content_pages': cards,
            'cards': program_cards(cards),
        }

    def get_context(self, value, parent_context=None):
        # imported here: research.models imports streams.blocks at module level
        from research.models import ThemePage

        context = super().get_context(value, parent_context)
        themes = ThemePage.objects.live().filter(archive=0).order_by('path')

        selected = value.get('programs')
        programs = []
        if selected:
            # Author-curated: exactly the chosen programs, in chooser order. Resolve
            # each one's theme (for accent + display label) via its ThemeProgram row.
            for entry in selected:
                program = entry.get('program')
                if not program:
                    continue
                program = program.specific
                if getattr(program, 'archive', 0) == 1:
                    continue
                membership = program.theme_memberships.select_related('theme').first()
                theme = membership.theme if membership else None
                title = membership.display_title if membership else program.title
                programs.append(self._spotlight_entry(program, theme, title, entry.get('content_pages')))
        else:
            # Auto: all live programs under each live theme, in taxonomy order.
            for theme in themes:
                for row in theme.theme_programs.select_related('program').all():
                    program = row.program
                    if not program.live or program.archive == 1:
                        continue
                    programs.append(self._spotlight_entry(program, theme, row.display_title))

        context['spotlight_themes'] = themes
        context['spotlight_programs'] = programs
        return context

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(ProgramSpotlightBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'program_spotlight_block')

    class Meta:
        icon = 'site'
        label = 'Program Spotlight'
        template = 'streams/program_spotlight_block.html'


def populated_pages(mode, auto_queryset, manual_value, count):
    """Resolve a content-list module's pages from its population-mode control.

    The content counterpart to ``selected_or_auto`` — the reusable resolver for the
    ``mode``/``count``/``items`` control trio (Program Grid first; later content
    carousels/bentos reuse it):

    - ``manual`` → exactly the author's hand-picked pages (live + specific, in
      chooser order), via ``selected_or_auto``.
    - ``auto`` (or anything else) → the first ``count`` of ``auto_queryset``, which
      the module pre-filters and orders (e.g. a program's live content,
      newest-first). ``.specific()`` it upstream so the card presenter stays cheap.

    Always returns a list.
    """
    if mode == 'manual':
        return selected_or_auto(manual_value) or []
    return list(auto_queryset[:count])


def resolve_program(program_source, program_value, page):
    """Resolve a program-module's program (the shared first half of every program
    module's author controls):

    - ``manual`` → the author's chosen ``research.ProjectPage``.
    - ``auto`` → the page the module is placed on, when that page itself *is* a
      program (a ``ProjectPage``) — e.g. a Programs Carousel dropped on a program
      page picks up that program automatically.

    Returns a specific ``ProjectPage`` or ``None``. Pair with ``populated_pages``
    for the cards (auto most-recent vs manual hand-picked), scoped to this program.
    """
    from research.models import ProjectPage
    if program_source == 'auto':
        specific = page.specific if page else None
        return specific if isinstance(specific, ProjectPage) else None
    # Default (manual, or legacy data with no program_source): the chooser.
    return program_value.specific if program_value else None


def scope_content_qs(qs, page):
    """Auto-scope a dynamic module's content queryset to the page it sits on
    (QA regroup decision 23:32 — uniform across all dynamic modules):

    - on a program page → only that program's tagged content;
    - on a theme page   → content tagged to any of the theme's programs;
    - anywhere else     → unchanged (site-wide).

    Applies to AUTO population only — manual hand-picked lists stay as authored.
    ``qs`` must be a ``ContentPage`` queryset (or an MTI child, e.g. EventPage /
    ArticlePage — the ``projects`` M2M is inherited)."""
    from research.models import ProjectPage, ThemePage
    # Program pages are ContentPages too (they carry a publishing_date), so a
    # site-wide "latest" rail surfaced them as "Topic" cards beside real
    # resources (Jennifer/Tia, BugHerd #436/#437 — the DPH rails). Taxonomy is
    # never a resource: drop programs before any scoping. Only a queryset whose
    # model is an ancestor of ProjectPage (ContentPage / Page) can hold one —
    # EventPage etc. have no `projectpage` relation and would raise.
    if issubclass(ProjectPage, qs.model):
        qs = qs.exclude(projectpage__isnull=False)
    specific = page.specific if page else None
    if isinstance(specific, ProjectPage):
        return qs.filter(projects=specific)
    if isinstance(specific, ThemePage):
        program_ids = list(specific.theme_programs.values_list('program_id', flat=True))
        return qs.filter(projects__in=program_ids).distinct() if program_ids else qs.none()
    return qs


def manual_programs(value):
    """The authored multi-program list (BugHerd #62) — the composable ``programs``
    ListBlock any program module can carry. Returns specific live ProjectPages,
    in chooser order."""
    return [p.specific for p in (value.get('programs') or []) if p and p.live]


def program_card_pills(page):
    """The ``pills`` override for one card in a program module (Program Grid,
    Programs Carousel, Program Spotlight). Program modules never pill a program
    (BugHerd #519): a card that IS a program (a ProjectPage) gets ``[]`` — no pill
    row, where ``card_data`` would otherwise fall back to the program page's own
    topics; any other card gets ``None``, i.e. the item's own topic pills like
    every other content card."""
    from research.models import ProjectPage
    return [] if isinstance(getattr(page, 'specific', page), ProjectPage) else None


def program_cards(pages):
    """``[(page, pills)]`` for a program module's card loop (see
    ``program_card_pills``)."""
    return [(p, program_card_pills(p)) for p in pages]


def program_module_context(value, page):
    """Shared resolution for a program content module (Program Grid / Programs
    Carousel): resolve the program, its theme accent, and the populated content
    list. Returns a context dict with ``program``, ``accent`` (colour name),
    ``accent_class`` (surface accent modifier), ``pages`` and ``cards``
    (``pages`` paired with each card's pills, ``program_cards``).

    On a Theme page, ``auto`` flips meaning (BugHerd #62): there is no single
    "this page's program", so the module renders the theme's own programs as
    the cards — the full editorial ``theme_programs`` list, in order. A manual
    multi-program pick renders the same way: the chosen programs ARE the cards.
    """
    from research.models import ThemePage

    specific = page.specific if page else None
    if value.get('program_source') == 'auto' and isinstance(specific, ThemePage):
        programs = [
            tp.program.specific for tp in
            specific.theme_programs.select_related('program')
            if tp.program.live
        ][:value.get('count') or 3]  # respect the authored count (BugHerd #99)
        return {
            'program': None,
            'accent': specific.accent_colour,
            'accent_class': specific.accent_surface_class,
            'pages': programs,
            'cards': program_cards(programs),  # program cards: no pill row (#519)
        }

    picked = manual_programs(value) if value.get('program_source') != 'auto' else []
    if len(picked) > 1:
        # Manual multi-program pick (BugHerd #62): the chosen programs render as
        # the cards, exactly like the theme-auto branch. No single theme owns
        # the set, so no accent lock, and the program cards carry no pill row.
        return {
            'program': None,
            'accent': 'red',
            'accent_class': '',
            'pages': picked,
            'cards': program_cards(picked),
        }

    # A single pick in the multi-list behaves like the legacy one-program chooser.
    program = (picked[0] if picked else
               resolve_program(value.get('program_source'), value.get('program'), page))

    theme = None
    if program:
        membership = program.theme_memberships.select_related('theme').first()
        if membership:
            theme = membership.theme
    accent = theme.accent_colour if theme else 'red'

    auto_qs = (
        program.content_pages.live().public()
        .order_by('-publishing_date').specific()
    ) if program else []
    pages = populated_pages(
        value.get('mode'), auto_qs, value.get('items'), value.get('count') or 3,
    )

    return {
        'program': program,
        'accent': accent,
        'accent_class': theme.accent_surface_class if theme else '',
        'pages': pages,
        # Content cards show their own topics, not the program the module is
        # about — the section already names it. Hand-picked program pages (e.g.
        # /experts/ "Explore Our Research Areas") show no pill row (BugHerd #519).
        'cards': program_cards(pages),
    }


class ProgramGridBlock(ConditionalFieldsMixin, blocks.StructBlock, ThemeableBlock):
    """Dynamic module: a grid of content cards belonging to one program. The author
    chooses the program (which sets the section context and the theme accent) and
    how the grid is populated — ``auto`` (the program's most-recent live content) or
    ``manual`` (a hand-picked, ordered list). Cards are the shared ``media-vertical``
    archetype (accent-topped image + topic pills + title + serif excerpt + CTA);
    they never pill the program (BugHerd #519).

    The ``mode``/``count``/``items`` trio is the reusable population-mode control
    (resolved by ``populated_pages``); ``program`` is the module-specific source.
    """

    heading = blocks.CharBlock(required=False, help_text='Section heading (e.g. "Program Overview").')
    intro = blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False)
    program_source = blocks.ChoiceBlock(
        choices=[
            ('manual', 'Manual — choose a program'),
            ('auto', "Auto — use this page's program(s) (program and theme pages)"),
        ],
        default='manual',
        help_text='Where the program comes from. Auto uses the page the module is '
                  'placed on: on a program page it shows that program\'s content; '
                  'on a theme page it shows the theme\'s programs as cards.',
    )
    program = blocks.PageChooserBlock(
        page_type='research.ProjectPage',
        required=False,
        help_text='Manual source: the program this grid is about — sets the card '
                  'pills + theme accent, and (in auto-cards mode) the recent content.',
    )
    # Composable multi-program pick (BugHerd #62): two or more programs render
    # as the cards themselves, like the theme-auto grid.
    programs = blocks.ListBlock(
        blocks.PageChooserBlock(page_type='research.ProjectPage'),
        required=False, default=[],
        help_text='Manual source: pick several programs to show them as cards. '
                  'One program here behaves like the single chooser above.',
    )
    mode = blocks.ChoiceBlock(
        choices=[
            ('auto', 'Auto — most recent content'),
            ('manual', 'Manual — hand-picked content'),
        ],
        default='auto',
        label='Cards',
        help_text='How the cards are populated (scoped to the program above).',
    )
    count = blocks.IntegerBlock(
        default=3, min_value=1, max_value=12,
        label='Number of items (auto)',
        help_text="Auto cards: how many of the program's most-recent items to show.",
    )
    items = blocks.ListBlock(
        blocks.PageChooserBlock(page_type='core.ContentPage'),
        required=False,
        label='Items (manual)',
        help_text='Manual cards: choose and order the content to show.', default=[],
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        # Cards show their own topic pills (none on program-as-card grids), and
        # the theme accent classes each card so .ds-accent-media resolves the
        # right top-rule colour. See program_module_context.
        resolved = program_module_context(value, context.get('page'))
        context['grid_program'] = resolved['program']
        context['grid_cards'] = resolved['cards']
        context['grid_accent_class'] = resolved['accent_class']
        context['grid_pages'] = resolved['pages']
        return context

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(ProgramGridBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'program_grid_block')

    class Meta:
        icon = 'grid'
        label = 'Program Grid'
        template = 'streams/program_grid_block.html'


class ProgramsCarouselBlock(ConditionalFieldsMixin, SurfaceMixin, ThemeableBlock):
    """Dynamic module: a horizontal carousel of content cards for one program. Same
    data + author controls as the Program Grid (program auto/manual + cards
    auto/manual), rendered as a swipeable rail whose first cell is the section
    title (heading + a "View More" link to the program). Surface-aware (light /
    dark); each card carries its program's theme accent.
    """

    heading = blocks.CharBlock(required=False, help_text='Section heading (e.g. "Explore the Program").')
    intro = blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False)
    cta_label = blocks.CharBlock(
        required=False, default='View More',
        help_text='Label for the link to the program (in the title cell).',
    )
    cta_page = blocks.PageChooserBlock(
        required=False, label='View More link',
        help_text='Page the title-cell link points to; falls back to the '
                  'resolved program\'s page when empty (BugHerd #78).',
    )
    # A raw link wins over the page chooser — for destinations a chooser can't
    # express, e.g. a tab deep link like /programs/<slug>/?tab=research
    # (Tia, BugHerd #423; same field as the Resource Carousel's #336).
    cta_link = blocks.CharBlock(
        required=False, label='View More URL (overrides the page)',
        help_text='Path or URL, e.g. /programs/africas-digital-transformation/?tab=research.',
    )
    program_source = blocks.ChoiceBlock(
        choices=[
            ('manual', 'Manual — choose a program'),
            ('auto', "Auto — use this page's program(s) (program and theme pages)"),
        ],
        default='manual',
        help_text='Where the program comes from. Auto uses the page the module is '
                  'placed on: on a program page it shows that program\'s content; '
                  'on a theme page it shows the theme\'s programs as cards.',
    )
    program = blocks.PageChooserBlock(
        page_type='research.ProjectPage',
        required=False,
        help_text='Manual source: the program this carousel is about.',
    )
    # Composable multi-program pick (BugHerd #62) — same behaviour as the grid.
    programs = blocks.ListBlock(
        blocks.PageChooserBlock(page_type='research.ProjectPage'),
        required=False, default=[],
        help_text='Manual source: pick several programs to show them as cards. '
                  'One program here behaves like the single chooser above.',
    )
    mode = blocks.ChoiceBlock(
        choices=[
            ('auto', 'Auto — most recent content'),
            ('manual', 'Manual — hand-picked content'),
        ],
        default='auto',
        label='Cards',
        help_text='How the cards are populated (scoped to the program above).',
    )
    count = blocks.IntegerBlock(
        default=9, min_value=1, max_value=24,
        label='Number of items (auto)',
        help_text="Auto cards: how many of the program's most-recent items to show.",
    )
    items = blocks.ListBlock(
        blocks.PageChooserBlock(page_type='core.ContentPage'),
        required=False,
        label='Items (manual)',
        help_text='Manual cards: choose and order the content to show.', default=[],
    )
    show_pagination = blocks.BooleanBlock(required=False, default=True, label='Show pagination')
    loop = blocks.BooleanBlock(
        required=False, default=True,
        help_text='Return to the first slide after the last (needs at least 4 slides).',
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        resolved = program_module_context(value, context.get('page'))
        context['carousel_program'] = resolved['program']
        context['carousel_cards'] = resolved['cards']
        context['carousel_accent_class'] = resolved['accent_class']
        context['carousel_pages'] = resolved['pages']
        # get_url(request) — bare .url emits the Site's absolute root_url off-prod
        # (see core/cards.py card_data).
        cta_page = value.get('cta_page')
        if value.get('cta_link'):
            # Raw link wins (BugHerd #423) — tab deep links a chooser can't hold.
            context['view_more_url'] = value['cta_link']
        elif cta_page:
            context['view_more_url'] = cta_page.get_url(context.get('request'))
        else:
            context['view_more_url'] = resolved['program'].get_url(context.get('request')) if resolved['program'] else None
        # Outline buttons (card CTA + View More) aren't surface-aware — pick the
        # scheme from the surface (light → red-on-light; any colour/dark → on-dark).
        context['cta_scheme'] = 'on-light' if value.get('surface') == 'light' else 'on-dark'
        return context

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(ProgramsCarouselBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'programs_carousel_block')

    class Meta:
        icon = 'list-ul'
        label = 'Programs Carousel'
        label_format = '{heading}'  # collapsed/minimap label shows the heading, not the surface (BugHerd #92)
        template = 'streams/programs_carousel_block.html'


class ExpertsGridBlock(ConditionalFieldsMixin, SurfaceMixin, ThemeableBlock):
    """Dynamic module: a paginated 3-up grid of expert cards. Authors choose the
    experts — ``auto`` (all live experts, A–Z) or ``manual`` (a hand-picked,
    ordered list) — and which card slots show (role / bio / expertise / latest
    activity). Cards stagger in on scroll (animation-guide); the grid pages
    client-side (``per_page``). Surface-aware (dark default).
    """

    heading = blocks.CharBlock(required=False, help_text='Section heading (e.g. "Experts").')
    intro = blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False)
    cta_label = blocks.CharBlock(required=False, default='View All Experts')
    cta_page = blocks.PageChooserBlock(
        required=False, label='View-all link',
        help_text='Optional page the "View All Experts" button links to (e.g. the '
                  'experts listing). Hidden if empty.',
    )
    mode = blocks.ChoiceBlock(
        choices=[
            ('auto', 'Auto — all live experts (A–Z)'),
            ('manual', 'Manual — hand-picked experts'),
        ],
        default='auto',
        label='Experts',
        help_text='How the grid is populated.',
    )
    count = blocks.IntegerBlock(
        default=24, min_value=1, max_value=60,
        label='Maximum experts (auto)',
        help_text='Auto mode: cap on how many experts to load (paged below).',
    )
    experts = blocks.ListBlock(
        blocks.PageChooserBlock(page_type='people.PersonPage'),
        required=False,
        label='Experts (manual)',
        help_text='Manual mode: choose and order the experts to show.', default=[],
    )
    per_page = blocks.IntegerBlock(
        default=9, min_value=3, max_value=24,
        help_text='How many cards per page (paged client-side). Multiples of 3 keep full rows.',
    )
    card_slots = ExpertCardSlotsBlock()

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)

        context['experts'] = resolve_experts(
            value.get('mode'), value.get('experts'), value.get('count'),
            program=host_program(parent_context))
        context['per_page'] = value.get('per_page') or 9
        context['cta_url'] = value['cta_page'].get_url(context.get('request')) if value.get('cta_page') else None
        context['cta_scheme'] = 'on-light' if value.get('surface') == 'light' else 'on-dark'
        return context

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(ExpertsGridBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'experts_grid_block')

    class Meta:
        icon = 'group'
        label = 'Experts Grid'
        label_format = '{heading}'  # collapsed/minimap label shows the heading, not the surface (BugHerd #92)
        template = 'streams/experts_grid_block.html'


# Seniority tiers for a program's experts tab (BugHerd #133). Juode's ranking:
# senior experts (directors) first, then distinguished > senior > fellows, then
# managers/advisors, then everyone else. Matched against the free-text `position`,
# first pattern wins, so a compound title ranks by its most senior part
# ("Distinguished Fellow and Director of ..." ranks as a director).
EXPERT_SENIORITY_PATTERNS = (
    ('director', 0),
    ('distinguished fellow', 1),
    ('senior fellow', 2),
    ('fellow', 3),
    ('manager', 4),
    ('advisor', 4),
    ('adviser', 4),
    ('associate', 4),
)
EXPERT_SENIORITY_LAST = 5  # blank positions, former holders, anything unmatched

# CIGI's own president never appears on a program's experts tab — only on the team
# pages (Juode, BugHerd #133). Matched narrowly on purpose: a bare "president"
# test would also drop external experts who lead other organisations, e.g.
# "President, The Brookings Institution" or "President of Iceland".
CIGI_PRESIDENT_PATTERNS = ('president of cigi', 'president, cigi', 'cigi president')


def is_cigi_president(person):
    position = (getattr(person, 'position', '') or '').lower()
    return any(p in position for p in CIGI_PRESIDENT_PATTERNS)


def expert_seniority(person):
    """Tier a person by their free-text position. Lower sorts first."""
    position = (getattr(person, 'position', '') or '').lower()
    # A former holder ranks last whatever the rest of the title says.
    if position.startswith('former'):
        return EXPERT_SENIORITY_LAST
    for needle, tier in EXPERT_SENIORITY_PATTERNS:
        if needle in position:
            return tier
    return EXPERT_SENIORITY_LAST


def host_program(parent_context):
    """The ProjectPage a module is rendering on, else None. Lets a program page
    scope its own dynamic modules without an author setting (BugHerd #133)."""
    page = (parent_context or {}).get('page')
    from research.models import ProjectPage
    return page if isinstance(page, ProjectPage) else None


def resolve_experts(mode, manual_value, count, program=None):
    """Resolve an expert-list module's people from its source control. ``manual`` →
    the hand-picked PersonPages (live + specific, in order); ``auto`` → all live
    experts (``person_types=4``) A–Z, capped at ``count`` with expertise prefetched.
    Shared by the Experts Grid + Experts Carousel.

    ``program`` scopes auto mode to the experts tied to that program, and orders
    them by seniority instead of A–Z (BugHerd #133). Tied means either an author
    credit on live content linked to the program, or a direct program link on the
    person. A–Z still breaks ties inside each seniority tier.
    """
    if mode == 'manual':
        return [p.specific for p in (manual_value or []) if p and getattr(p, 'live', False)]
    from django.db.models import Prefetch, Q
    from people.models import PersonPage
    from core.models import ContentPageAuthor
    # Prefetch the data expert_data() reads per person, so expert lists don't N+1:
    # derived_topics (expertise pills), projects (programs pills), and the latest
    # authored live page (as `_live_authored`, pre-filtered + ordered so
    # expert_data takes [0] instead of a per-person query).
    qs = (
        PersonPage.objects.live().public()
        .filter(person_types=4, archive=0)  # person_types=4 = Expert
        .order_by('last_name', 'first_name')
        .prefetch_related(
            'derived_topics__program_theme',
            'projects',
            Prefetch(
                'content_pages_as_author',
                queryset=ContentPageAuthor.objects.filter(content_page__live=True)
                .select_related('content_page')
                .order_by('-content_page__publishing_date'),
                to_attr='_live_authored',
            ),
        )
    )

    if mode == 'random':
        # Featured Experts rail (Tim, BugHerd #251): a random pull per visit,
        # restricted to Research Directors and Distinguished Fellows — the role
        # types people migration 0063 seeded and backfilled (BugHerd #359).
        from core.faceted_listing import PERSON_TYPE_IDS
        return list(
            qs.filter(person_types__id__in=[
                PERSON_TYPE_IDS['research_director'],
                PERSON_TYPE_IDS['distinguished_fellow'],
            ]).distinct().order_by('?')[:count or 12]
        )

    if program is None:
        return list(qs[:count or 24])

    # Tied to the program: an author credit on live content linked to it, or a
    # direct program link on the person.
    author_ids = ContentPageAuthor.objects.filter(
        content_page__projects=program, content_page__live=True,
    ).values_list('author_id', flat=True)
    people = list(qs.filter(Q(id__in=author_ids) | Q(projects=program)).distinct())
    # CIGI's president belongs to the team pages, not a program's experts tab
    # (Juode, BugHerd #133).
    people = [p for p in people if not is_cigi_president(p)]
    # Sort AFTER the query, not in SQL: seniority reads the free-text position, and
    # the cap has to apply to the ranked list so it never drops a director.
    people.sort(key=expert_seniority)  # stable, so the A–Z order survives per tier
    return people[:count or 24]


class ExpertsCarouselBlock(ConditionalFieldsMixin, SurfaceMixin, ThemeableBlock):
    """Dynamic module: a horizontal carousel of expert cards — the rail sibling of
    the Experts Grid. The first cell is the section title (heading + intro + a
    "View All Experts" link); the rest are expert cards (auto = all live experts
    A–Z; manual = hand-picked). Cards stagger in on scroll and crop the headshot on
    hover (animation-guide). Surface-aware (dark default).
    """

    heading = blocks.CharBlock(required=False, help_text='Section heading (e.g. "Experts").')
    intro = blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False)
    cta_label = blocks.CharBlock(required=False, default='View All Experts')
    cta_page = blocks.PageChooserBlock(
        required=False, label='View-all link',
        help_text='Optional page the "View All Experts" button links to. Hidden if empty.',
    )
    mode = blocks.ChoiceBlock(
        choices=[
            ('auto', 'Auto — all live experts (A–Z)'),
            # Random per visit, Research Directors + Distinguished Fellows only
            # (Tim, BugHerd #251 — the A–Z rail always led with the same faces).
            ('random', 'Random — Research Directors & Distinguished Fellows, shuffled per visit'),
            ('manual', 'Manual — hand-picked experts'),
        ],
        default='auto',
        label='Experts',
        help_text='How the rail is populated.',
    )
    count = blocks.IntegerBlock(
        default=12, min_value=1, max_value=40,
        label='Maximum experts (auto)',
        help_text='Auto mode: cap on how many experts to load into the rail.',
    )
    experts = blocks.ListBlock(
        blocks.PageChooserBlock(page_type='people.PersonPage'),
        required=False,
        label='Experts (manual)',
        help_text='Manual mode: choose and order the experts to show.', default=[],
    )
    card_slots = ExpertCardSlotsBlock()
    show_pagination = blocks.BooleanBlock(required=False, default=True, label='Show pagination')
    loop = blocks.BooleanBlock(
        required=False, default=True,
        help_text='Return to the first slide after the last (needs at least 4 slides).',
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        context['experts'] = resolve_experts(
            value.get('mode'), value.get('experts'), value.get('count'),
            program=host_program(parent_context))
        context['cta_url'] = value['cta_page'].get_url(context.get('request')) if value.get('cta_page') else None
        context['cta_scheme'] = 'on-light' if value.get('surface') == 'light' else 'on-dark'
        return context

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(ExpertsCarouselBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'experts_carousel_block')

    class Meta:
        icon = 'group'
        label = 'Experts Carousel'
        label_format = '{heading}'  # collapsed/minimap label shows the heading, not the surface (BugHerd #92)
        template = 'streams/experts_carousel_block.html'


class ResourceCarouselBlock(ConditionalFieldsMixin, SurfaceMixin, ThemeableBlock):
    """Dynamic module: a swipeable rail of resources (any content type). The first
    cell is the section title (heading + intro + "View All"); then one feature card
    (image + pill + date + title + excerpt) followed by columns of two stacked
    compact cards (same, no image). Resources: ``auto`` (most-recent live content)
    or ``manual`` (hand-picked). Surface-aware (light default).
    """

    heading = blocks.CharBlock(required=False, help_text='Section heading (e.g. "Explore Recommended").')
    intro = blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False)
    cta_label = blocks.CharBlock(required=False, default='View All')
    cta_page = blocks.PageChooserBlock(
        required=False, label='View-all link',
        help_text='Optional page the "View All" button links to. Hidden if empty.',
    )
    # A raw link wins over the page chooser — for destinations a chooser can't
    # express, e.g. a tab deep link like /digital-policy-hub/?tab=working-papers
    # (John + Tia, BugHerd #336).
    cta_link = blocks.CharBlock(
        required=False, label='View-all URL (overrides the page)',
        help_text='Path or URL, e.g. /digital-policy-hub/?tab=working-papers.',
    )
    mode = blocks.ChoiceBlock(
        choices=[
            ('auto', 'Auto — most recent content'),
            ('manual', 'Manual — hand-picked content'),
        ],
        default='auto',
        label='Resources',
        help_text='How the rail is populated.',
    )
    # Auto-mode scope (BugHerd #437): the DPH "Featured Working Papers" rail
    # pulled whatever was recent site-wide — events and topic pages included.
    # Same content-type toggles as the bento (#120), plus a publication-type
    # narrowing for rails like "working papers only".
    content_types = blocks.MultipleChoiceBlock(
        choices=[
            ('opinion', 'Opinions'),
            ('publication', 'Publications'),
            ('multimedia', 'Multimedia'),
        ],
        required=False,
        help_text='Auto mode: the content types this rail includes. '
                  'Empty = any content type.',
    )
    # Choices mirror core.faceted_listing.PUBLICATION_TYPES (kept literal, as
    # that block keeps them, because the module imports lazily).
    publication_type = blocks.ChoiceBlock(
        choices=[
            ('working-paper', 'Working Paper'),
            ('policy-briefs', 'Policy Briefs'),
            ('cigi-papers', 'CIGI Papers'),
            ('special-reports', 'Special Reports'),
            ('books', 'Books'),
        ],
        required=False,
        help_text='Auto mode: restrict the publications in this rail to one '
                  'publication type (other selected content types are untouched).',
    )
    count = blocks.IntegerBlock(
        default=9, min_value=1, max_value=30,
        label='Number of items (auto)',
        help_text='Auto mode: how many of the most-recent items to show.',
    )
    items = blocks.ListBlock(
        blocks.PageChooserBlock(page_type='core.ContentPage'),
        required=False,
        label='Items (manual)',
        help_text='Manual mode: choose and order the resources to show.', default=[],
    )
    show_pagination = blocks.BooleanBlock(required=False, default=True, label='Show pagination')
    loop = blocks.BooleanBlock(
        required=False, default=True,
        help_text='Return to the first slide after the last (needs at least 4 slides).',
    )

    def get_context(self, value, parent_context=None):
        from django.db.models import Q
        from core.faceted_listing import RESOURCE_TYPE_MODELS
        from core.models import ContentPage
        from core.queries import live_dated
        context = super().get_context(value, parent_context)
        # Auto content scopes to the program/theme page this module sits on
        # (QA regroup decision 23:32).
        auto_qs = scope_content_qs(
            live_dated(ContentPage.objects), (parent_context or {}).get('page'))
        # Author-set scope (BugHerd #437) — see the field comments above.
        allowed = [t for t in (value.get('content_types') or []) if t in RESOURCE_TYPE_MODELS]
        # A publication type with no content types means "publications of this
        # type" (Tia, BugHerd #436: Working Paper alone still pulled events) —
        # the isnull branch below only applies when other types are selected.
        if value.get('publication_type') and not allowed:
            allowed = ['publication']
        if allowed:
            auto_qs = auto_qs.filter(
                content_type__model__in=[RESOURCE_TYPE_MODELS[t] for t in allowed])
        if value.get('publication_type'):
            auto_qs = auto_qs.filter(
                Q(publicationpage__isnull=True)
                | Q(publicationpage__publication_type__slug=value['publication_type']))
        auto_qs = auto_qs.specific()
        pages = populated_pages(value.get('mode'), auto_qs, value.get('items'), value.get('count') or 9)
        context['feature'] = pages[0] if pages else None
        # One compact card per slide — no stacked pairs (BugHerd #68, Juode).
        context['compact_cards'] = pages[1:]
        request = (parent_context or {}).get('request')
        # An authored raw link beats the page chooser (BugHerd #336).
        context['cta_url'] = (
            value.get('cta_link')
            or (value['cta_page'].get_url(request=request) if value.get('cta_page') else None)
        )
        context['cta_scheme'] = 'on-light' if value.get('surface') == 'light' else 'on-dark'
        return context

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(ResourceCarouselBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'resource_carousel_block')

    class Meta:
        icon = 'list-ul'
        label = 'Resource Carousel'
        label_format = '{heading}'  # collapsed/minimap label shows the heading, not the surface (BugHerd #92)
        template = 'streams/resource_carousel_block.html'


class ResourceBentoBlock(ConditionalFieldsMixin, SurfaceMixin, ThemeableBlock):
    """Dynamic module: a bento of resources — one large feature card (image + pill
    + date + title + excerpt) beside a divided column of compact cards (pill +
    title + type-of-content + optional thumb). Resources ``auto`` (most-recent) or
    ``manual``. Surface-aware (light default).
    """

    heading = blocks.CharBlock(required=False, help_text='Section heading.')
    intro = blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False)
    cta_label = blocks.CharBlock(required=False, default='View All')
    cta_page = blocks.PageChooserBlock(
        required=False, label='View-all link',
        help_text='Optional page the "View All" button links to. Hidden if empty.',
    )
    # BugHerd #493 — ticket ref stays in the code comment; help_text is editor-facing.
    cta_link = blocks.CharBlock(
        required=False, label='View-all URL',
        help_text='Use instead of the page chooser above when the link needs a query '
                  'string or points off-site, e.g. /programs/example/?tab=research. '
                  'When set, this wins over the chosen page.')
    mode = blocks.ChoiceBlock(
        choices=[
            ('auto', 'Auto — most recent content'),
            ('manual', 'Manual — hand-picked content'),
        ],
        default='auto',
        label='Resources',
        help_text='How the bento is populated.',
    )
    # Auto-mode content-type toggles (BugHerd #120): the KP's Opinions bento
    # holds op-eds only, but auto pulled whatever was recent — program pages
    # included. Same control the faceted listing carries; events never appear
    # regardless (BugHerd #123 — they belong to the event modules).
    content_types = blocks.MultipleChoiceBlock(
        choices=[
            ('opinion', 'Opinions'),
            ('publication', 'Publications'),
            ('multimedia', 'Multimedia'),
            # Opt-in only (BugHerd #433 — the /events/ "Featured Events" bento
            # had no way to hold events). Auto's default still excludes them
            # (#123): unticked, events never appear.
            ('event', 'Events'),
        ],
        required=False,
        help_text='Auto mode: the content types this bento includes. '
                  'Empty = all resource types except events; tick Events to '
                  'include them.',
    )
    # DPH working papers led the homepage bento on recency alone (Tim,
    # BugHerd #425) — an author-set exclusion, so general bentos can keep
    # publications while dropping the hub's papers.
    exclude_working_papers = blocks.BooleanBlock(
        required=False, default=False,
        label='Exclude working papers',
        help_text='Auto mode: leave out Working Paper publications (the DPH papers).',
    )
    # Auto-mode news-type filter (BugHerd #188): the media-and-news bento needs to
    # pull "CIGI in the News" posts specifically. content_types picks page MODELS,
    # so it can't express an ArticlePage subtype — this is the separate axis.
    # Choices mirror core.faceted_listing.NEWS_TYPES (kept literal here, as
    # news_prefilter does, because that module imports lazily).
    news_types = blocks.MultipleChoiceBlock(
        choices=[
            ('news-release', 'CIGI News'),
            ('cigi-in-the-news', 'CIGI in the News'),
            ('op-eds', 'Opinion-Eds'),
        ],
        required=False,
        label='News types',
        help_text='Auto mode: restrict the bento to these news types. '
                  'Empty = no news filter.',
    )
    count = blocks.IntegerBlock(
        default=5, min_value=2, max_value=9,
        label='Number of items (auto)',
        help_text='Auto mode: total items — 1 feature + the rest as the compact column.',
    )
    items = blocks.ListBlock(
        blocks.PageChooserBlock(page_type='core.ContentPage'),
        required=False,
        label='Items (manual)',
        help_text='Manual mode: choose and order the resources (first = feature).', default=[],
    )
    layout = blocks.ChoiceBlock(
        choices=[
            ('split', 'Feature + list'),
            ('centered', 'Feature centred between two lists'),
            ('duo', 'Two features + list'),
        ],
        default='split',
        help_text='Split — one feature card beside a single compact column. '
                  'Centred — the feature flanked by two compact columns. '
                  'Duo — two feature cards beside one compact column '
                  '(homepage light bento).',
    )
    show_header = blocks.BooleanBlock(
        required=False, default=True, label='Show header',
        help_text='Show the heading / intro / View-all row above the bento.',
    )
    show_date = blocks.BooleanBlock(
        required=False, default=True, label='Show date',
        help_text='Show each item’s date on the cards.',
    )
    show_author = blocks.BooleanBlock(
        required=False, default=True, label='Show author',
        help_text='Show author name(s), linked to their bio page.',
    )

    def get_context(self, value, parent_context=None):
        from core.models import ContentPage
        from core.queries import live_dated
        context = super().get_context(value, parent_context)
        # Auto content scopes to the program/theme page this module sits on
        # (QA regroup decision 23:32).
        base = scope_content_qs(
            live_dated(ContentPage.objects), (parent_context or {}).get('page'))
        # Auto mode pulls events ONLY when the author ticks the Events type
        # (BugHerd #433, relaxing #123's blanket exclusion — the /events/
        # "Featured Events" bento needs them). Untouched configs keep the #123
        # behaviour: no events. Manual mode keeps whatever the author picks.
        count = value.get('count') or 5
        # Author-set content-type toggles (BugHerd #120): empty = all resource
        # types. Filters through the same model mapping the faceted listing
        # uses, so 'opinion' means ArticlePage etc.
        from core.faceted_listing import RESOURCE_TYPE_MODELS, NEWS_TYPE_SLUGS
        allowed = [t for t in (value.get('content_types') or []) if t in RESOURCE_TYPE_MODELS]
        if 'event' not in allowed:
            base = base.exclude(eventpage__isnull=False)
        if value.get('exclude_working_papers'):
            # BugHerd #425 — see the field comment above.
            base = base.exclude(publicationpage__publication_type__slug='working-paper')
        if allowed:
            base = base.filter(content_type__model__in=[RESOURCE_TYPE_MODELS[t] for t in allowed])
        else:
            # No toggles picked → all RESOURCE types, and only resource types.
            # ContentPage also covers program/theme/basic pages, and a recently
            # edited ProjectPage was leading the homepage bento (BugHerd #220).
            base = base.filter(content_type__model__in=[
                'articlepage', 'publicationpage', 'multimediapage'])
        # Author-set news types (BugHerd #188). Selecting any restricts the bento
        # to ArticlePages of those types, so the media-and-news bento can hold
        # "CIGI in the News" posts only. Empty leaves the catalogue untouched.
        news = [t for t in (value.get('news_types') or []) if t in NEWS_TYPE_SLUGS]
        if news:
            base = base.filter(articlepage__article_type__slug__in=news)
        auto_qs = list(base[:count].specific())
        pages = populated_pages(value.get('mode'), auto_qs, value.get('items'), count)
        # Duo layout leads with two feature cards.
        n_features = 2 if value.get('layout') == 'duo' else 1
        if value.get('mode') != 'manual':
            # Auto mode: the feature slots are image-led cards — an imageless
            # page there collapses the column to
            # empty surface. Promote the first image-bearing pages into the
            # feature slots; everything else keeps its recency order in the
            # compact column. Manual mode keeps the author's order (first =
            # feature is the documented contract).
            from core.cards import _card_image
            with_img = [p for p in pages if _card_image(p)]
            if len(with_img) >= n_features:
                features = with_img[:n_features]
                pages = features + [p for p in pages if p not in features]
        context['feature'] = pages[0] if pages else None
        context['features'] = pages[:n_features]
        compact = pages[n_features:]
        if value.get('layout') == 'duo':
            # KP (BugHerd #31): the duo list column holds three resources.
            compact = compact[:3]
        context['compact_cards'] = compact
        # Centred layout (KP 1557-52706, BugHerd #7): a fixed 2-card image-led
        # left column (media-stacked), the rest in the right compact column.
        context['compact_left'] = compact[:2]
        context['compact_right'] = compact[2:]
        # Mobile carousel (BugHerd #56): one flat, ordered list of every card —
        # the visual stack order — swiped as a rail at <=768. Same nodes' data,
        # rendered as its own partial (the desktop grid can't double as a Swiper).
        feature = context['feature']
        if value.get('layout') == 'duo':
            context['mobile_cards'] = list(context['features']) + list(compact)
        elif value.get('layout') == 'centered':
            context['mobile_cards'] = (list(context['compact_left'])
                                       + ([feature] if feature else [])
                                       + list(context['compact_right']))
        else:
            context['mobile_cards'] = ([feature] if feature else []) + list(compact)
        # Relative path, not the .url property (absolute prod host off-prod).
        cta_page = value.get('cta_page')
        # An authored raw link beats the page chooser — a tab deep link like
        # /programs/<slug>/?tab=research has no page to choose (BugHerd #493,
        # same rule as the resource carousel's cta_link, #336).
        context['cta_url'] = (
            value.get('cta_link')
            or ((cta_page.get_url_parts() or [None, None, None])[2] if cta_page else None))
        context['cta_scheme'] = 'on-light' if value.get('surface') == 'light' else 'on-dark'
        return context

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(ResourceBentoBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'resource_bento_block')

    class Meta:
        icon = 'grip'
        label = 'Resource Bento'
        label_format = '{heading}'  # collapsed/minimap label shows the heading, not the surface (BugHerd #92)
        template = 'streams/resource_bento_block.html'


class EventsCarouselBlock(ConditionalFieldsMixin, SurfaceMixin, ThemeableBlock):
    """Dynamic module: a swipeable rail of event cards under a section header
    (heading + intro + "View all"). Events ``auto`` (most-recent live events) or
    ``manual`` (hand-picked). Cards are the shared ``event`` variant. Surface-aware
    (light default).
    """

    heading = blocks.CharBlock(required=False, help_text='Section heading (e.g. "Events").')
    intro = blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False)
    cta_label = blocks.CharBlock(required=False, default='View all')
    cta_page = blocks.PageChooserBlock(
        required=False, label='View-all link',
        help_text='Optional page the "View all" link points to. Hidden if empty.',
    )
    mode = blocks.ChoiceBlock(
        choices=[
            ('auto', 'Auto — most recent events'),
            ('manual', 'Manual — hand-picked events'),
        ],
        default='auto',
        label='Events',
        help_text='How the rail is populated.',
    )
    count = blocks.IntegerBlock(
        default=9, min_value=1, max_value=30,
        label='Number of events (auto)',
        help_text='Auto mode: how many of the most-recent events to show.',
    )
    items = blocks.ListBlock(
        blocks.PageChooserBlock(page_type='events.EventPage'),
        required=False,
        label='Events (manual)',
        help_text='Manual mode: choose and order the events to show.', default=[],
    )
    show_pagination = blocks.BooleanBlock(required=False, default=True, label='Show pagination')
    loop = blocks.BooleanBlock(
        required=False, default=True,
        help_text='Return to the first slide after the last (needs at least 4 slides).',
    )

    def get_context(self, value, parent_context=None):
        from django.utils import timezone
        from events.models import EventPage
        context = super().get_context(value, parent_context)
        # Auto events scope to the program/theme page this module sits on
        # (QA regroup decision 23:32).
        base = scope_content_qs(
            EventPage.objects.live().public().filter(publishing_date__isnull=False),
            (parent_context or {}).get('page'))
        # Event-date order, soonest upcoming first (BugHerd #10, Juode) — a
        # publish-date order buries next week's event under one published for
        # next year. Past events follow, most recent first.
        # (EventPage.publishing_date IS the event start datetime.)
        now = timezone.now()
        count = value.get('count') or 9
        auto_qs = (
            list(base.filter(publishing_date__gte=now).order_by('publishing_date')[:count])
            + list(base.filter(publishing_date__lt=now).order_by('-publishing_date')[:count])
        )
        context['events'] = populated_pages(
            value.get('mode'), auto_qs, value.get('items'), value.get('count') or 9)
        request = (parent_context or {}).get('request')
        context['cta_url'] = value['cta_page'].get_url(request=request) if value.get('cta_page') else None
        context['cta_scheme'] = 'on-light' if value.get('surface') == 'light' else 'on-dark'
        return context

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(EventsCarouselBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'events_carousel_block')

    class Meta:
        icon = 'date'
        label = 'Events Carousel'
        label_format = '{heading}'  # collapsed/minimap label shows the heading, not the surface (BugHerd #92)
        template = 'streams/events_carousel_block.html'


class NewsCarouselBlock(ConditionalFieldsMixin, SurfaceMixin, ThemeableBlock):
    """Dynamic module: a swipeable rail of news cards (shared media-vertical
    card) under a section header. Serves CIGI News + In the News. Design
    inferred per direction (2026-07-03): the only design artifact is the
    wireframe (image card: type row, pill, title, excerpt,
    button); layout/styling reuses the events carousel. Auto (most recent
    news) or manual.
    """

    heading = blocks.CharBlock(required=False, help_text='Section heading (e.g. "In the News").')
    intro = blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False)
    cta_label = blocks.CharBlock(required=False, default='View all')
    cta_page = blocks.PageChooserBlock(
        required=False, label='View-all link',
        help_text='Optional page the "View all" link points to. Hidden if empty.',
    )
    mode = blocks.ChoiceBlock(
        choices=[
            ('auto', 'Auto — most recent news'),
            ('manual', 'Manual — hand-picked items'),
        ],
        default='auto',
        label='News items',
    )
    count = blocks.IntegerBlock(
        default=9, min_value=1, max_value=30,
        label='Number of items (auto)',
    )
    items = blocks.ListBlock(
        blocks.PageChooserBlock(page_type='articles.ArticlePage'),
        required=False,
        label='News items (manual)', default=[],
    )
    show_pagination = blocks.BooleanBlock(required=False, default=True, label='Show pagination')
    loop = blocks.BooleanBlock(
        required=False, default=True,
        help_text='Return to the first slide after the last (needs at least 4 slides).',
    )

    def get_context(self, value, parent_context=None):
        from articles.models import ArticlePage
        context = super().get_context(value, parent_context)
        # Auto news scopes to the program/theme page this module sits on
        # (QA regroup decision 23:32).
        auto_qs = scope_content_qs(
            ArticlePage.objects.live().public()
            .filter(article_type__title__in=['CIGI in the News', 'News Releases'],
                    publishing_date__isnull=False)
            .order_by('-publishing_date'),
            (parent_context or {}).get('page'))
        context['news_items'] = populated_pages(
            value.get('mode'), auto_qs, value.get('items'), value.get('count') or 9)
        request = (parent_context or {}).get('request')
        context['cta_url'] = value['cta_page'].get_url(request=request) if value.get('cta_page') else None
        context['cta_scheme'] = 'on-light' if value.get('surface') == 'light' else 'on-dark'
        return context

    class Meta:
        icon = 'doc-empty'
        label = 'News Carousel'
        label_format = '{heading}'  # collapsed/minimap label shows the heading, not the surface (BugHerd #92)
        template = 'streams/news_carousel_block.html'


class NewsGridBlock(ConditionalFieldsMixin, SurfaceMixin, ThemeableBlock):
    """Dynamic module: a 2-up grid of news items as media-compact cards (pill +
    title + type-of-content + optional thumb), under a section title (heading-left
    / intro right). The redesigned "News Carousel" (now a grid — the "Explore" /
    "In the News" grid). Auto = most-recent "CIGI in the News" articles;
    manual = hand-picked. Surface-aware (light default).
    """

    heading = blocks.CharBlock(required=False, default='In the News', help_text='Section heading.')
    intro = blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False)
    # Author-set button row, the shared ButtonBlock (BugHerd #164).
    buttons = blocks.ListBlock(ButtonBlock(), required=False, default=[])
    mode = blocks.ChoiceBlock(
        choices=[
            ('auto', 'Auto — most recent "In the News"'),
            ('manual', 'Manual — hand-picked'),
        ],
        default='auto',
        label='Items',
        help_text='How the grid is populated.',
    )
    # DPH hub scope (Jennifer, BugHerd #439): the hub's Latest News must show
    # DPH items only, and the hub page carries no program to auto-scope by.
    # Flagged articles (ArticlePage.is_dph_news, admin-only) replace the
    # "CIGI in the News" pull entirely — the DPH feed mixes article types.
    dph_only = blocks.BooleanBlock(
        required=False, default=False,
        label='DPH news only',
        help_text='Auto mode: show articles flagged "DPH news item" instead of '
                  '"CIGI in the News".',
    )
    count = blocks.IntegerBlock(
        default=6, min_value=2, max_value=24,
        label='Number of items (auto)',
        help_text='Auto mode: how many of the most-recent "In the News" items to show.',
    )
    items = blocks.ListBlock(
        blocks.PageChooserBlock(page_type='core.ContentPage'),
        required=False,
        label='Items (manual)',
        help_text='Manual mode: choose and order the items to show.', default=[],
    )

    def get_context(self, value, parent_context=None):
        from articles.models import ArticlePage
        context = super().get_context(value, parent_context)
        if value.get('dph_only'):
            # BugHerd #439 — see the field comment above.
            auto_qs = (ArticlePage.objects.live().public()
                       .filter(is_dph_news=True)
                       .order_by('-publishing_date').specific())
            context['cards'] = populated_pages(
                value.get('mode'), auto_qs, value.get('items'), value.get('count') or 6)
            return context
        # Auto news scopes to the program/theme page this module sits on
        # (QA regroup decision 23:32).
        auto_qs = scope_content_qs(
            ArticlePage.objects.live().public()
            .filter(article_type__title='CIGI in the News')
            .order_by('-publishing_date'),
            (parent_context or {}).get('page')).specific()
        context['cards'] = populated_pages(
            value.get('mode'), auto_qs, value.get('items'), value.get('count') or 6)
        return context

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(NewsGridBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'news_grid_block')

    class Meta:
        icon = 'doc-full'
        label = 'News Grid (In the News)'
        label_format = '{heading}'  # collapsed/minimap label shows the heading, not the surface (BugHerd #92)
        template = 'streams/news_grid_block.html'


class TrendingIssuesBlock(ConditionalFieldsMixin, SurfaceMixin, ThemeableBlock):
    """Dynamic module: a slim banner spotlighting one trending piece of content —
    icon + title + excerpt + author + date + a "Read More" link. The item is
    ``manual`` (hand-picked) or ``auto`` (most-recent live content). Surface-aware
    (light default).
    """

    mode = blocks.ChoiceBlock(
        choices=[
            ('manual', 'Manual — choose the item'),
            ('auto', 'Auto — most recent content'),
        ],
        default='manual',
        label='Item',
    )
    item = blocks.PageChooserBlock(
        page_type='core.ContentPage', required=False,
        help_text='Manual mode: the content to spotlight.',
    )
    cta_label = blocks.CharBlock(required=False, default='Read More')

    def get_context(self, value, parent_context=None):
        from core.models import ContentPage
        from core.queries import live_dated
        context = super().get_context(value, parent_context)
        page = None
        if value.get('mode') == 'manual':
            chosen = value.get('item')
            page = chosen.specific if chosen and chosen.live else None
        if page is None and value.get('mode') == 'auto':
            # Auto pick scopes to the program/theme page this module sits on
            # (QA regroup decision 23:32).
            page = scope_content_qs(
                live_dated(ContentPage.objects),
                (parent_context or {}).get('page')).specific().first()

        trending = None
        if page:
            request = (parent_context or {}).get('request')
            authorship = page.authors.first()
            excerpt = getattr(page, 'feature_subtitle', '') \
                or strip_tags(getattr(page, 'subtitle', '') or '').strip()
            trending = {
                'title': page.title,
                'url': page.get_url(request=request),
                'excerpt': excerpt,
                'author': authorship.author.title if authorship and authorship.author else '',
                'date': getattr(page, 'publishing_date', None),
            }
        context['trending'] = trending
        context['cta_scheme'] = 'on-light' if value.get('surface') == 'light' else 'on-dark'
        return context

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(TrendingIssuesBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'trending_issues_block')

    class Meta:
        icon = 'pick'
        label = 'Trending Issues'
        label_format = 'Trending Issues'  # collapsed/minimap label shows the heading, not the surface (BugHerd #92)
        template = 'streams/trending_issues_block.html'


class JobsListBlock(ConditionalFieldsMixin, SurfaceMixin, ThemeableBlock):
    """Dynamic module: a section title (heading + intro) over a list of job
    postings — each row is closing date + title, a description, and a "View
    Opportunity" link, divided by rules. Jobs ``auto`` (all live postings, by
    closing date) or ``manual``. Surface-aware (light default).
    """

    heading = blocks.CharBlock(required=False, help_text='Section heading (e.g. "Find Your Place").')
    intro = blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False)
    # No per-row label field: it sat above the section's button row and read as
    # a second button setting (Tia, BugHerd #184 — "can we remove the funny Cta
    # Label above the button option"). Each row's link is a fixed "View
    # Opportunity" in the template; `buttons` is the authorable row.
    buttons = blocks.ListBlock(ButtonBlock(), required=False, default=[])

    mode = blocks.ChoiceBlock(
        choices=[
            ('auto', 'Auto — all open postings (by closing date)'),
            ('manual', 'Manual — hand-picked postings'),
        ],
        default='auto',
        label='Postings',
    )
    count = blocks.IntegerBlock(
        default=10, min_value=1, max_value=50,
        label='Maximum postings (auto)',
    )
    items = blocks.ListBlock(
        blocks.PageChooserBlock(page_type='careers.JobPostingPage'),
        required=False,
        label='Postings (manual)',
        help_text='Manual mode: choose and order the job postings to show.', default=[],
    )

    def get_context(self, value, parent_context=None):
        from careers.models import JobPostingPage
        context = super().get_context(value, parent_context)
        if value.get('mode') == 'manual':
            jobs = [p.specific for p in (value.get('items') or []) if p and getattr(p, 'live', False)]
        else:
            jobs = list(
                JobPostingPage.objects.live().public()
                .order_by(models.F('closing_date').asc(nulls_last=True))[:value.get('count') or 10]
            )
        context['jobs'] = jobs
        return context

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(JobsListBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'jobs_list_block')

    class Meta:
        icon = 'list-ul'
        label = 'Jobs List'
        label_format = '{heading}'  # collapsed/minimap label shows the heading, not the surface (BugHerd #92)
        template = 'streams/jobs_list_block.html'


class VideoTextBlock(blocks.StructBlock, ThemeableBlock):
    """Section title (heading + intro) above a full-bleed video. The video is a
    facade — a poster image with a play button that loads the embed on click
    (YouTube/Vimeo). Stacked layout (text on top, video below).
    """

    heading = blocks.CharBlock(required=False)
    intro_text = blocks.RichTextBlock(
        features=['bold', 'italic', 'link', 'ol', 'ul'],
        required=False,
    )
    buttons = blocks.ListBlock(ButtonBlock(), required=False, default=[])
    poster_image = ImageChooserBlock(required=True, help_text='Thumbnail shown before the video plays.')
    video_file = VideoBlock(required=False, help_text='Upload a video file. Takes precedence over a video URL.')
    video_url = blocks.URLBlock(required=False, help_text='YouTube or Vimeo URL. Used if no file is uploaded.')

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(VideoTextBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'video_text_block')

    class Meta:
        icon = 'media'
        label = 'Video + Text'
        template = 'streams/video_text_block.html'


class BannerBlock(SurfaceMixin, ThemeableBlock):
    """Slim full-width announcement bar: accent top rule, heading + description
    on the left, a button on the right. Surface-aware (accent colours the rule).
    Every element has an enable/disable toggle so authors can show/hide each
    independently without losing its content.
    """

    show_rule = blocks.BooleanBlock(required=False, default=True, label='Show top rule')
    show_heading = blocks.BooleanBlock(required=False, default=True, label='Show heading')
    heading = blocks.CharBlock(required=False)
    show_description = blocks.BooleanBlock(required=False, default=True, label='Show description')
    description = blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False)
    show_buttons = blocks.BooleanBlock(required=False, default=True, label='Show button(s)')
    buttons = blocks.ListBlock(ButtonBlock(), required=False, default=[])

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(BannerBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'banner_block')

    class Meta:
        icon = 'warning'
        label = 'Banner'
        label_format = '{heading}'  # collapsed/minimap label shows the heading, not the surface (BugHerd #92)
        template = 'streams/banner_block.html'


class GallerySlideBlock(blocks.StructBlock):
    """A single gallery slide: image + optional caption."""

    image = ImageChooserBlock(required=True)
    caption = blocks.CharBlock(required=False)

    class Meta:
        icon = 'image'
        label = 'Slide'


class GalleryTextBlock(SurfaceMixin, ThemeableBlock):
    """Section title (heading + intro + optional button row) above an image
    carousel (Swiper coverflow: centred larger active slide, captions, prev/next
    nav + pagination). Surface-aware (BugHerd #157) — defaults inherit the page,
    so existing placements are unchanged.
    """

    heading = blocks.CharBlock(required=False)
    intro_text = blocks.RichTextBlock(
        features=['bold', 'italic', 'link', 'ol', 'ul'],
        required=False,
    )
    buttons = blocks.ListBlock(ButtonBlock(), required=False, default=[])
    slides = blocks.ListBlock(GallerySlideBlock())

    # Carousel controls (shared across all DS carousels)
    show_pagination = blocks.BooleanBlock(required=False, default=True, help_text='Show the pagination dots/numbers.')
    loop = blocks.BooleanBlock(required=False, default=True, help_text='Return to the first slide after the last (needs at least 4 slides).')
    autoplay = blocks.BooleanBlock(required=False, default=False, help_text='Advance slides automatically.')
    autoplay_speed = blocks.IntegerBlock(required=False, default=5, min_value=1, help_text='Seconds between slides when autoplay is on.')

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(GalleryTextBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'gallery_text_block')

    class Meta:
        icon = 'image'
        label = 'Gallery + Text'
        template = 'streams/gallery_text_block.html'


class SupportingMaterialBlock(blocks.StructBlock):
    """A single downloadable/material card: title, content-type label, link."""

    title = blocks.CharBlock(required=True)
    content_type = blocks.CharBlock(required=False, help_text='Small label, e.g. "Working Paper".')
    link_page = blocks.PageChooserBlock(required=False)
    link_document = DocumentChooserBlock(required=False)
    link_url = blocks.CharBlock(required=False, help_text='Used if no page/document is set.')
    button_label = blocks.CharBlock(required=False, help_text='Card button text. Defaults to "Read More".')

    class Meta:
        icon = 'doc-full'
        label = 'Material'


class SupportingMaterialsBlock(ConditionalFieldsMixin, blocks.StructBlock, ThemeableBlock):
    """Section title over a horizontal card carousel of downloadable materials.
    Reuses the shared carousel (nav + numbered pagination). Always visible — no
    collapsed state (per the animation guide), despite the chevron in the design.
    """

    heading = blocks.CharBlock(required=False)
    intro_text = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
    )
    items = blocks.ListBlock(SupportingMaterialBlock())

    # Carousel controls (shared across all DS carousels)
    show_pagination = blocks.BooleanBlock(required=False, default=True, help_text='Show the pagination dots/numbers.')
    loop = blocks.BooleanBlock(required=False, default=True, help_text='Return to the first slide after the last (needs at least 4 slides).')
    autoplay = blocks.BooleanBlock(required=False, default=False, help_text='Advance slides automatically.')
    autoplay_speed = blocks.IntegerBlock(required=False, default=5, min_value=1, help_text='Seconds between slides when autoplay is on.')

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(SupportingMaterialsBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'supporting_materials_block')

    class Meta:
        icon = 'list-ul'
        label = 'Supporting Material Carousel'
        template = 'streams/supporting_materials_block.html'


class PersonBlock(blocks.PageChooserBlock, ThemeableBlock):

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(PersonBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'person_block')

    def get_api_representation(self, value, context=None):
        if value:
            return {
                'id': value.id,
                'title': value.title,
                'url': value.url,
            }

    class Meta:
        icon = 'user'
        label = 'Person'


class AutoPlayVideoBlock(blocks.StructBlock, ThemeableBlock):
    video = VideoBlock(required=False)
    caption = blocks.CharBlock(required=False)

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(AutoPlayVideoBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'autoplay_video_block')

    class Meta:
        icon = 'media'
        label = 'Autoplay Video'
        template = 'streams/autoplay_video_block.html'


class BlockQuoteBlock(blocks.StructBlock, ThemeableBlock):
    """Block quote paragraph with optional image and link"""

    quote = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=True,
    )
    quote_author = blocks.CharBlock(required=False)
    author_title = blocks.CharBlock(required=False)
    image = ImageChooserBlock(required=False)
    link_url = blocks.URLBlock(required=False)
    link_text = blocks.CharBlock(required=False)

    implemented_themes = [
        'after_covid_series_opinion',
        'cyber_series_opinion',
        'health_security_series_opinion',
        'ai_series_opinion',
        'john_holmes_series_opinion',
    ]

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(BlockQuoteBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'block_quote_block')

    class Meta:
        icon = 'openquote'
        label = 'Blockquote Paragraph'
        template = 'streams/block_quote_block.html'


class BookPurchaseLinkBlock(blocks.StructBlock, ThemeableBlock):
    url = blocks.URLBlock(required=True)
    link_text = blocks.CharBlock(required=True)

    def get_api_representation(self, value, context=None):
        if value:
            return {
                'url': value.url,
                'link_text': value.link_text,
            }

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(BookPurchaseLinkBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'book_purchase_link_block')

    class Meta:
        icon = 'link'
        label = 'Purchase Link'


class ChartBlock(blocks.StructBlock, ThemeableBlock):
    """Chart image with title"""

    title = blocks.CharBlock(required=False)
    image = ImageChooserBlock(required=True)
    hide_image_caption = blocks.BooleanBlock(required=False)
    full_width = blocks.BooleanBlock(required=False)

    implemented_themes = [
        'cyber_series_opinion',
        'pfpc_series_opinion',
    ]

    def get_template(self, value, context, *args, **kwargs):
        standard_template = 'streams/chart_block.html'
        return self.get_theme_template(standard_template, context, 'chart_block')

    class Meta:
        icon = 'image'
        label = 'Chart'
        template = 'streams/chart_block.html'


class ContactEmailBlock(blocks.EmailBlock):
    class Meta:
        icon = 'mail'
        label = 'Contact Email'
        template = 'streams/contact_email_block.html'


class ContactPersonBlock(blocks.PageChooserBlock):
    class Meta:
        icon = 'user'
        label = 'Contact Person'
        template = 'streams/contact_person_block.html'


class CTABlock(blocks.StructBlock, ThemeableBlock):
    class CTAText(models.TextChoices):
        DOWNLOAD = ('Download', 'Download')
        DOWNLOAD_PDF = ('Download PDF', 'Download PDF')
        EXPLORE_SERIES = ('Explore Series', 'Explore Series')

    class CTAIcon(models.TextChoices):
        NO_ICON = ('', 'No Icon')
        DOWNLOAD = ('fas fa-download', 'Download')
        POINTER = ('fas fa-mouse-pointer', 'Pointer')

    file = DocumentChooserBlock(required=False)
    link = blocks.CharBlock(required=False, help_text="This will only work if no file is uploaded.")
    button_text = blocks.ChoiceBlock(required=False, choices=CTAText.choices, max_length=32)
    button_icon = blocks.ChoiceBlock(required=False, choices=CTAIcon.choices, default=CTAIcon.NO_ICON, max_length=32)

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(CTABlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'cta_block')

    class Meta:
        icon = 'view'
        label = 'Call to Action'


class EditorBlock(blocks.PageChooserBlock, ThemeableBlock):

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(EditorBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'editor_block')

    def get_api_representation(self, value, context=None):
        if value:
            return {
                'id': value.id,
                'title': value.title,
                'url': value.url,
            }

    class Meta:
        icon = 'user'
        label = 'Editor'


class EmbeddedMultimediaBlock(blocks.StructBlock, ThemeableBlock):
    multimedia_url = blocks.URLBlock(required=True)
    title = blocks.CharBlock(required=False)

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(EmbeddedMultimediaBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'embedded_multimedia_block')

    class Meta:
        icon = 'media'
        label = 'Embedded Multimedia'
        template = 'streams/embedded_multimedia_block.html'


class EmbeddedVideoBlock(blocks.StructBlock, ThemeableBlock):
    video_url = blocks.URLBlock(required=True)
    caption = blocks.CharBlock(required=False)
    image = ImageChooserBlock(required=False)
    aspect_ratio = blocks.ChoiceBlock(choices=[
        ('none', 'None'),
        ('landscape', 'Landscape'),
        ('square', 'Square'),
    ])

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(EmbeddedVideoBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'embedded_video_block')

    class Meta:
        icon = 'media'
        label = 'Embedded Video'
        template = 'streams/embedded_video_block.html'


class ExternalPersonBlock(blocks.CharBlock):
    class Meta:
        icon = 'user'
        label = 'External Person'


class ExternalQuoteBlock(blocks.StructBlock, ThemeableBlock):
    """External quote with optional source"""

    quote = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=True,
    )
    source = blocks.CharBlock(required=False)

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(ExternalQuoteBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'external_quote_block')

    class Meta:
        icon = 'edit'
        label = 'External Quote'
        template = 'streams/external_quote_block.html'


class ExternalVideoStructBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True)
    video_url = blocks.URLBlock(required=True)

    class Meta:
        icon = 'media'
        label = 'External Video'


class ExternalVideoBlock(blocks.ListBlock, ThemeableBlock):
    def __init__(self, *args, **kwargs):
        super(ExternalVideoBlock, self).__init__(ExternalVideoStructBlock, *args, **kwargs)

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(ExternalVideoBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'external_video_block')

    class Meta:
        icon = 'media'
        label = 'External Video Block'
        template = 'streams/external_video_block.html'


class ExtractBlock(blocks.RichTextBlock, ThemeableBlock):
    def __init__(
        self, required=True, help_text=None, editor="default", features=None, **kwargs
    ):
        super().__init__(**kwargs)
        self.features = [
            'bold',
            'dropcap',
            'endofarticle',
            'paragraph_heading',
            'h2',
            'h3',
            'h4',
            'hr',
            'image',
            'italic',
            'link',
            'ol',
            'subscript',
            'superscript',
            'ul',
            'anchor',
        ]

    implemented_themes = [
        'space_series_opinion',
    ]

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(ExtractBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'extract_block')

    class Meta:
        icon = 'edit'
        label = 'Extract'
        template = 'streams/extract_block.html'


class ImageBlock(blocks.StructBlock, ThemeableBlock):
    """Image"""

    image = ImageChooserBlock(required=True)
    hide_image_caption = blocks.BooleanBlock(required=False)
    link = blocks.URLBlock(required=False)

    implemented_themes = [
        'cyber_series_opinion',
        'data_series_opinion',
        'longform_2_opinion',
        'space_series_opinion',
        'dph_page',
    ]

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(ImageBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'image_block')

    class Meta:
        icon = 'image'
        label = 'Image'
        template = 'streams/image_block.html'


class ImageScrollBlock(blocks.StructBlock, ThemeableBlock):
    """Image Scroll"""

    image = ImageChooserBlock(required=True)
    hide_image_caption = blocks.BooleanBlock(required=False)

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(ImageScrollBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'image_scroll_block')

    class Meta:
        icon = 'image'
        label = 'Image'
        template = 'streams/image_scroll_block.html'


class ImageFullBleedBlock(blocks.StructBlock, ThemeableBlock):
    """Full bleed image"""

    image = ImageChooserBlock(required=True)
    hide_image_caption = blocks.BooleanBlock(required=False)

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(ImageFullBleedBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'image_full_bleed_block')

    class Meta:
        icon = 'image'
        label = 'Full Bleed Image'
        template = 'streams/image_full_bleed_block.html'


class InlineVideoBlock(blocks.PageChooserBlock, ThemeableBlock):
    """Inline video"""

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(InlineVideoBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'inline_video_block')

    class Meta:
        icon = 'media'
        label = 'Inline Video'
        template = 'streams/inline_video_block.html'


class HeroLinkBlock(blocks.StructBlock):
    hero_link_text = blocks.CharBlock(required=True)
    hero_link_url = blocks.CharBlock(required=True)
    hero_link_icon = blocks.CharBlock(required=False, help_text='Use a font-awesome icon name such as fa-envelope')

    class Meta:
        icon = 'link'
        label = 'Hero Link'
        template = 'streams/hero_link_block.html'


class HeroDocumentBlock(blocks.StructBlock):
    hero_link_text = blocks.CharBlock(required=True)
    hero_link_document = DocumentChooserBlock(required=True)
    hero_link_icon = blocks.CharBlock(required=False, help_text='Use a font-awesome icon name such as fa-envelope')

    class Meta:
        icon = 'doc-full'
        label = 'Hero Document'
        template = 'streams/hero_document_block.html'


class HighlightTitleBlock(blocks.CharBlock, ThemeableBlock):
    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(HighlightTitleBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'highlight_title_block')

    class Meta:
        icon = 'title'
        label = 'Highlight Title'
        template = 'streams/highlight_title_block.html'


class ParagraphBlock(blocks.RichTextBlock, ThemeableBlock):
    """Standard text paragraph."""

    def __init__(
        self, required=True, help_text=None, editor="default", features=None, **kwargs
    ):
        super().__init__(**kwargs)
        self.features = [
            'bold',
            'dropcap',
            'endofarticle',
            'paragraph_heading',
            'h2',
            'h3',
            'h4',
            'hr',
            'image',
            'italic',
            'underline',
            'link',
            'ol',
            'subscript',
            'superscript',
            'ul',
            'anchor',
            'rtl',
        ]

    implemented_themes = [
        'cyber_series_opinion_series',
        'data_series_opinion_series',
        'innovation_series_opinion_series',
        'longform_opinion_series',
        'platform_governance_series_opinion_series',
        'women_and_trade_series_opinion_series',
        'big_tech_s3_multimedia_series',
        'indigenous_lands_series_opinion_series',
        'dph_page',
    ]

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(ParagraphBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'paragraph_block')

    class Meta:
        icon = 'edit'
        label = 'Paragraph'
        template = 'streams/paragraph_block.html'


class PosterBlock(blocks.PageChooserBlock, ThemeableBlock):
    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(PosterBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'poster_block')

    class Meta:
        icon = 'form'
        label = 'Poster Teaser'
        template = 'streams/poster_block.html'


class ReadMoreBlock(blocks.StructBlock, ThemeableBlock):
    title = blocks.CharBlock(required=True)
    text = blocks.RichTextBlock(
        features=[
            'bold',
            'h3',
            'h4',
            'italic',
            'link',
            'ol',
            'ul',
        ],
        required=True,
    )

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(ReadMoreBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'read_more_block')

    class Meta:
        icon = 'edit'
        label = 'Read More'
        template = 'streams/read_more_block.html'


class RecommendedBlock(blocks.PageChooserBlock, ThemeableBlock):
    """Recommended content block"""

    implemented_themes = [
        'longform_2_opinion',
    ]

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(RecommendedBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'recommended_block')

    class Meta:
        icon = 'redirect'
        label = 'Recommended'
        template = 'streams/recommended_block.html'


class PDFDownloadBlock(blocks.StructBlock, ThemeableBlock):
    file = DocumentChooserBlock(required=True)
    button_text = blocks.CharBlock(
        required=False,
        help_text='Optional text to replace the button text. If left empty, the button will read "Download PDF".'
    )
    display = blocks.BooleanBlock(default=True)

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(PDFDownloadBlock, self).get_template(context, value, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'pdf_download_block')

    def get_api_representation(self, value, context=None):
        if value:
            return {
                'button_text': value.get('button_text'),
                'url': value.get('file').file.url,
            }

    class Meta:
        icon = 'download-alt'
        label = 'PDF Download'


class EPubDownloadBlock(blocks.StructBlock, ThemeableBlock):
    file = DocumentChooserBlock(required=True)
    button_text = blocks.CharBlock(
        required=False,
        help_text='Optional text to replace the button text. If left empty, the button will read "Download Book".'
    )
    display = blocks.BooleanBlock(default=True)

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(EPubDownloadBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'epub_download_block')

    def get_api_representation(self, value, context=None):
        if value:
            return {
                'button_text': value.get('button_text'),
                'url': value.get('file').file.url,
            }

    class Meta:
        icon = 'download-alt'
        label = 'ePub Download'


class PullQuoteLeftBlock(blocks.StructBlock, ThemeableBlock):
    """Pull quote left side"""

    quote = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=True,
    )
    quote_author = blocks.CharBlock(required=False)
    author_title = blocks.CharBlock(required=False)

    implemented_themes = [
        'data_series_opinion',
        'longform_2_opinion',
        'ai_ethics_series_opinion',
    ]

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(PullQuoteLeftBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'pull_quote_left_block')

    class Meta:
        icon = 'edit'
        label = 'Pull Quote Left'
        template = 'streams/pull_quote_left_block.html'


class PullQuoteRightBlock(blocks.StructBlock, ThemeableBlock):
    """Pull quote right side"""

    quote = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=True,
    )
    quote_author = blocks.CharBlock(required=False)
    author_title = blocks.CharBlock(required=False)

    implemented_themes = [
        'data_series_opinion',
        'longform_2_opinion',
        'ai_ethics_series_opinion',
    ]

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(PullQuoteRightBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'pull_quote_right_block')

    class Meta:
        icon = 'edit'
        label = 'Pull Quote Right'
        template = 'streams/pull_quote_right_block.html'


class TableStreamBlock(TableBlock):
    class Meta:
        icon = 'form'
        label = 'Table'
        template = 'streams/table_block.html'


class TableStreamBlockV2(blocks.StructBlock, ThemeableBlock):
    """Table block with optional caption"""

    title = blocks.CharBlock(required=False)
    table = TableStreamBlock(required=True)

    def render(self, value, context=None):
        if context is None:
            context = {}

        # Get rendered HTML for the table block
        table_block = self.child_blocks['table']
        table_html = table_block.render(value['table'], context=context)

        new_context = dict(context)
        new_context.update({
            'self': value,
            'title': value.get('title'),
            'rendered_table': table_html,
        })

        return render_to_string(self.get_template(value, context), new_context)

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(TableStreamBlockV2, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'table_block')

    class Meta:
        icon = 'form'
        label = 'Table Block V2'
        template = 'streams/table_block_v2.html'


class TextBackgroundBlock(blocks.RichTextBlock, ThemeableBlock):
    """Text box with background colour """

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(TextBackgroundBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'text_background_block')

    class Meta:
        icon = 'edit'
        label = 'Text Background Block'
        template = 'streams/text_background_block.html'


class TextBorderBlock(blocks.StructBlock, ThemeableBlock):
    """Text box with border and optional colour for border """

    text = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=True,
    )
    border_colour = blocks.CharBlock(required=False)

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(TextBorderBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'text_border_block')

    class Meta:
        icon = 'edit'
        label = 'Bordered Text Block'
        template = 'streams/text_border_block.html'


class TooltipBlock(blocks.StructBlock, ThemeableBlock):
    """Tooltip block"""

    anchor = blocks.CharBlock(required=True)
    text = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=True,
    )
    name = blocks.CharBlock(required=False)
    title = blocks.CharBlock(required=False)
    image = ImageChooserBlock(required=False)

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(TooltipBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'tool_tip_block')

    class Meta:
        icon = 'warning'
        label = 'Tooltip Block'
        template = 'streams/tool_tip_block.html'


class TweetBlock(blocks.StructBlock, ThemeableBlock):
    """Tweet Block"""

    tweet_url = blocks.URLBlock(
        required=True,
        help_text='The URL of the tweet. Example: https://x.com/CIGIonline/status/1188821562440454144',
        verbose_name='Tweet URL',
    )

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(TweetBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'tweet_block')

    class Meta:
        icon = 'social'
        label = 'Tweet'
        template = 'streams/tweet_block.html'


class NewsletterBlock(blocks.StructBlock):
    class CallToActionChoices(models.TextChoices):
        EXPLORE = ('explore', 'Explore')
        FOLLOW = ('follow', 'Follow')
        LEARN_MORE = ('learn_more', 'Learn More')
        LISTEN = ('listen', 'Listen')
        NO_CTA = ('no_cta', 'No CTA')
        PDF = ('pdf', 'PDF')
        READ = ('read', 'Read')
        RSVP = ('rsvp', 'RSVP')
        SHARE_FACEBOOK = ('share_facebook', 'Share (Facebook)')
        SHARE_LINKEDIN = ('share_linkedin', 'Share (LinkedIn)')
        SHARE_TWITTER = ('share_twitter', 'Share (Twitter)')
        SUBSCRIBE = ('subscribe', 'Subscribe')
        WATCH = ('watch', 'Watch')

    def cta_image_link(self, cta):
        cta_image_links = {
            'watch': 'https://gallery.mailchimp.com/3cafbe8a8401ae9ed275d2f75/images/14d48b17-21b0-449a-81dd-3476baa65712.png',
            'read': 'https://gallery.mailchimp.com/3cafbe8a8401ae9ed275d2f75/images/27c0957b-671e-4a91-b4a4-dc43c63446e1.png',
            'pdf': 'https://gallery.mailchimp.com/3cafbe8a8401ae9ed275d2f75/images/599997d4-6b93-ad64-450e-3e848ff2eb09.png',
            'share_facebook': 'https://gallery.mailchimp.com/3cafbe8a8401ae9ed275d2f75/images/43333018-a716-1500-6eb7-92aa71454507.png',
            'share_twitter': 'https://gallery.mailchimp.com/3cafbe8a8401ae9ed275d2f75/images/0794410e-335b-375c-0c23-9007997a6288.png',
            'share_linkedin': 'https://gallery.mailchimp.com/3cafbe8a8401ae9ed275d2f75/images/044e1d7a-f595-dbc5-9915-950b06351a0a.png',
            'rsvp': 'https://gallery.mailchimp.com/3cafbe8a8401ae9ed275d2f75/images/44282420-4212-477f-b678-5783c82dc51c.png',
            'listen': 'https://gallery.mailchimp.com/3cafbe8a8401ae9ed275d2f75/images/cff5d5c0-f14f-4c58-86b6-1d20c77dc09e.png',
            'explore': 'https://gallery.mailchimp.com/3cafbe8a8401ae9ed275d2f75/images/4b5ad389-bfb3-4819-8732-3eaf95e4965e.png',
            'subscribe': '',
            'learn_more': 'https://gallery.mailchimp.com/3cafbe8a8401ae9ed275d2f75/images/4b5ad389-bfb3-4819-8732-3eaf95e4965e.png',
            'follow': 'https://gallery.mailchimp.com/3cafbe8a8401ae9ed275d2f75/images/3f938efb-c700-56b5-c3a8-3df53809e69e.png',
        }

        return cta_image_links[cta]

    def cta_text(self, cta):
        cta_texts = {
            'explore': 'Explore',
            'follow': 'Follow',
            'learn_more': 'Learn More',
            'listen': 'Listen',
            'pdf': 'PDF',
            'read': 'Read',
            'rsvp': 'RSVP',
            'share_facebook': 'Share',
            'share_linkedin': 'Share',
            'share_twitter': 'Share',
            'subscribe': 'Subscribe',
            'watch': 'Watch',
        }
        return cta_texts[cta]

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        context['url'] = value.get('url')
        context['text'] = value.get('text')

        if value.get('cta') and value.get('cta') != 'no_cta':
            context['cta_image_link'] = self.cta_image_link(value.get('cta'))
            context['cta_text'] = self.cta_text(value.get('cta')).upper()

        if value.get('image'):
            if value.get('image').file.url.endswith('.gif'):
                context['image_url'] = f'{context["page"].get_site().root_url}{settings.STATIC_URL}{value.get("image").file.name}'
                context['image_url_large'] = f'{context["page"].get_site().root_url}{settings.STATIC_URL}{value.get("image").file.name}'
            else:
                context['image_url'] = f'{context["page"].get_site().root_url}{settings.STATIC_URL}{value.get("image").get_rendition("fill-1200x476").file.name}'
                context['image_url_large'] = f'{context["page"].get_site().root_url}{settings.STATIC_URL}{value.get("image").get_rendition("fill-1200x595").file.name}'

        if value.get('content'):
            content_page = value.get('content').specific
            content_type = 'other'
            if hasattr(content_page, 'contenttype'):
                content_type = content_page.contenttype

            context['title'] = value.get('title_override') if value.get('title_override') else content_page.title
            if value.get('text_override'):
                context['text'] = value.get('text_override')
            elif content_type == 'other':
                context['text'] = ''
            elif (content_type == 'Opinion' or content_type == 'Publication') and content_page.short_description:
                context['text'] = content_page.short_description

            if value.get('image_override'):
                if value.get('image_override').file.url.endswith('.gif'):
                    context['image_url'] = value.get("image_override").file.name
                    context['image_url_large'] = value.get("image_override").file.name
                else:
                    context['image_url'] = value.get("image_override").get_rendition("fill-1200x476").file.name
                    context['image_url_large'] = value.get("image_override").get_rendition("fill-1200x595").file.name
            elif content_type != 'other' and content_page.image_hero:
                if content_page.image_hero.file.url.endswith('.gif'):
                    context['image_url'] = content_page.image_hero.file.name
                    context['image_url_large'] = content_page.image_hero.file.name
                else:
                    context['image_url'] = content_page.image_hero.get_rendition("fill-1200x476").file.name
                    context['image_url_large'] = content_page.image_hero.get_rendition("fill-1200x595").file.name
                context['image_alt'] = content_page.image_hero.caption

            if context.get('image_url'):
                context['image_url'] = f'{context["page"].get_site().root_url}{settings.STATIC_URL}{context["image_url"]}'

            if context.get('image_url_large'):
                context['image_url_large'] = f'{context["page"].get_site().root_url}{settings.STATIC_URL}{context["image_url_large"]}'

            if not value.get('url'):
                context['url'] = content_page.full_url

            if content_type == 'Event' and context.get('text'):
                def construct_event_time():
                    date_delta = (content_page.event_end - content_page.publishing_date).days if content_page.event_end else 0
                    start = timezone.localtime(content_page.publishing_date, pytz.timezone(settings.TIME_ZONE)).strftime("%b. %-d")
                    end = timezone.localtime(content_page.event_end, pytz.timezone(settings.TIME_ZONE)).strftime("%b. %-d") if date_delta > 0 else ''
                    if date_delta > 1:
                        connective_string = ' to '
                    elif date_delta > 0:
                        connective_string = ' and '
                    else:
                        connective_string = ''
                    date_string = f'{start}{connective_string}{end}'
                    time_string = timezone.localtime(content_page.publishing_date, pytz.timezone(settings.TIME_ZONE)).strftime(" – %-I:%M %p")
                    return f'{date_string}{time_string}'.replace('AM', 'a.m.').replace('PM', 'p.m.').replace('May.', 'May')
                event_time = construct_event_time()
                event_time_zone = f' {content_page.time_zone_label}' if content_page.time_zone_label else ''
                event_location = f' – {content_page.location_city}' if content_page.location_city else ''
                event_country = f', {content_page.location_country}' if content_page.location_country else ''
                if 'is_html_string' not in context:
                    soup = BeautifulSoup(context['text'].source, "html.parser")
                    first_p = soup.find('p')
                    event_info_tag = soup.new_tag('b')
                    event_info_tag.string = f'{event_time}{event_time_zone}{event_location}{event_country}: '
                    first_p.insert(0, event_info_tag)

                    context['text'].source = str(soup)

        if context.get('text'):
            is_str = isinstance(context['text'], str)
            if is_str:
                text_soup = BeautifulSoup(context['text'], 'html.parser')
            else:
                text_soup = BeautifulSoup(rich_text.expand_db_html(context['text'].source), 'html.parser')
            for link in text_soup.findAll('a'):
                link['style'] = 'text-decoration: none; color: #ee1558;'
            if is_str:
                context['text'] = str(text_soup)
            else:
                context['text'] = mark_safe(str(text_soup))

        return context


class AdvertisementBlock(NewsletterBlock):
    title = blocks.CharBlock(required=False)
    text = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
    )
    url = blocks.URLBlock(required=True)
    image = ImageChooserBlock(required=False)
    cta = blocks.ChoiceBlock(
        choices=NewsletterBlock.CallToActionChoices.choices,
        verbose_name='CTA',
        required=True,
    )

    class Meta:
        icon = 'image'
        label = 'Advertisement'
        template = 'streams/newsletter/advertisement_block.html'


class AdvertisementBlockLarge(AdvertisementBlock):

    class Meta:
        icon = 'image'
        label = 'Advertisement'
        template = 'streams/newsletter/advertisement_block_large.html'


class ContentBlock(NewsletterBlock):
    content = blocks.PageChooserBlock(required=False)
    url = blocks.URLBlock(required=False)
    title_override = blocks.CharBlock(required=False)
    text_override = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
    )
    cta = blocks.ChoiceBlock(
        choices=NewsletterBlock.CallToActionChoices.choices,
        verbose_name='CTA',
        required=True,
    )
    line_separator_above = blocks.BooleanBlock(
        verbose_name='Add line separator above block',
        required=False,
    )

    class Meta:
        icon = 'doc-full'
        label = 'Content'
        template = 'streams/newsletter/content_block.html'


class FeaturedContentBlock(NewsletterBlock):
    content = blocks.PageChooserBlock(required=False)
    url = blocks.URLBlock(required=False)
    title_override = blocks.CharBlock(required=False)
    text_override = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
    )
    image_override = ImageChooserBlock(required=False)
    cta = blocks.ChoiceBlock(
        choices=NewsletterBlock.CallToActionChoices.choices,
        verbose_name='CTA',
        required=True,
    )

    class Meta:
        icon = 'doc-full'
        label = 'Featured Content'
        template = 'streams/newsletter/featured_content_block.html'


class FeaturedContentBlockLarge(FeaturedContentBlock):

    class Meta:
        icon = 'doc-full'
        label = 'Featured Content'
        template = 'streams/newsletter/featured_content_block_large.html'


class SocialBlock(NewsletterBlock):
    title = blocks.CharBlock(required=False)
    text = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
    )

    class Meta:
        icon = 'group'
        label = 'Recommended'
        template = 'streams/newsletter/social_block.html'


class TextBlock(NewsletterBlock):
    title = blocks.CharBlock(required=False)
    text = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
    )

    class Meta:
        icon = 'doc-full'
        label = 'Text'
        template = 'streams/newsletter/text_block.html'


class IgcTimelineBlock(blocks.StructBlock):
    date = blocks.CharBlock(required=True)
    title = blocks.CharBlock(required=False)
    body = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
    )
    location = blocks.CharBlock(required=False)
    countries_represented = ImageChooserBlock(required=False)
    outcomes = blocks.StreamBlock(
        [
            ('outcome', blocks.StructBlock([
                ('date', blocks.DateBlock(required=False)),
                ('text', blocks.RichTextBlock(
                    features=['bold', 'italic', 'link'],
                    required=False,
                )),
            ])),
        ],
        required=False,
    )
    witnesses = blocks.StreamBlock(
        [
            ('witness_date', blocks.StructBlock([
                ('date', blocks.DateBlock(required=False)),
                ('witnesses', blocks.StreamBlock(
                    [
                        ('witnesses_full_session', blocks.StructBlock([
                            ('title', blocks.CharBlock(required=False)),
                            ('witness_transcript', blocks.URLBlock(required=False)),
                            ('witness_video', blocks.URLBlock(required=False)),
                        ])),
                        ('witness', blocks.StructBlock([
                            ('name', blocks.CharBlock(required=False)),
                            ('title', blocks.CharBlock(required=False)),
                            ('witness_transcript', blocks.URLBlock(required=False)),
                            ('witness_video', blocks.URLBlock(required=False)),
                        ])),
                    ],
                )),
            ])),
        ],
        required=False,
    )

    class Meta:
        icon = 'arrows-up-down'
        label = 'IGC Timeline'
        template = 'streams/igc_timeline_block.html'


class TimelineGalleryBlock(blocks.StructBlock):
    timeline = blocks.StreamBlock(
        [
            ('slide', blocks.StructBlock(
                [
                    ('year', blocks.CharBlock()),
                    ('text', blocks.RichTextBlock()),
                    ('image', ImageChooserBlock()),
                ]
            ))
        ],
        required=False,
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context['years'] = [x.value['year'] for x in value.get('timeline')]

        return context

    class Meta:
        icon = 'image'
        label = 'Timeline Gallery'
        template = 'streams/timeline_gallery_block.html'


class SliderGalleryBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    slides = blocks.StreamBlock(
        [
            ('slide', blocks.StructBlock(
                [
                    ('image', ImageChooserBlock()),
                    ('caption', blocks.RichTextBlock(required=False)),
                ]
            ))
        ],
        required=False,
    )

    class Meta:
        icon = 'image'
        label = 'Slider Gallery'
        template = 'streams/slider_gallery_block.html'


class PodcastSubscribeButtonBlock(blocks.StructBlock):
    label = blocks.CharBlock(required=True)
    url = blocks.URLBlock(required=True)

    class Meta:
        icon = 'link'
        label = 'Podcast Subscribe Button'


class PodcastFollowButtonBlock(blocks.StructBlock):
    """A 'Follow' social link for a podcast series hero. ``platform`` maps to a
    Font Awesome brand glyph (e.g. twitter, instagram, linkedin, youtube)."""

    platform = blocks.CharBlock(
        required=True,
        help_text='Platform key for the icon, e.g. twitter, instagram, linkedin, youtube.',
    )
    url = blocks.URLBlock(required=True)

    class Meta:
        icon = 'site'
        label = 'Podcast Follow Button'


class PodcastHostBlock(blocks.StructBlock):
    host = blocks.PageChooserBlock(page_type='people.PersonPage', required=True)
    image = ImageChooserBlock(required=False)
    bio = blocks.RichTextBlock(required=False)

    class Meta:
        icon = 'user'
        label = 'Podcast Host'
        template = 'streams/podcast_host_block.html'


class PodcastGuestBlock(blocks.StructBlock):
    guest = blocks.CharBlock(required=False)
    guest_page = blocks.PageChooserBlock(page_type='people.PersonPage', required=False)
    image = ImageChooserBlock(required=False)
    bio = blocks.RichTextBlock(required=False)

    class Meta:
        icon = 'user'
        label = 'Podcast Guest'
        template = 'streams/podcast_guest_block.html'


class AdditionalImageBlock(blocks.StructBlock, ThemeableBlock):
    class PositionChoices(models.TextChoices):
        layer_0 = ('0', '0')
        layer_1 = ('1', '1')
        layer_2 = ('2', '2')
        layer_3 = ('3', '3')
        layer_4 = ('4', '4')
        layer_5 = ('5', '5')
        layer_6 = ('6', '6')

    class AnimationChoices(models.TextChoices):
        VERTICAL = ('vertical', 'Vertical')
        HORIZONTAL = ('horizontal', 'Horizontal')
        ZOOM = ('zoom', 'Zoom')
        MOUSE = ('mouse', 'Mouse')
        NONE = ('none', 'None')

    image = ImageChooserBlock(required=True)
    classes = blocks.CharBlock(required=False)
    position = blocks.ChoiceBlock(
        choices=PositionChoices.choices,
    )
    animation = blocks.ChoiceBlock(
        choices=AnimationChoices.choices,
        default=AnimationChoices.NONE,
    )
    speed = blocks.DecimalBlock(default=0)
    initial_top = blocks.IntegerBlock(default=0)
    initial_left = blocks.IntegerBlock(default=0)

    class Meta:
        icon = 'image'
        label = 'Additional Image'
        help_text = 'Additional images to be used only if the theme requires them.'


class AdditionalDisclaimerBlock(blocks.StructBlock):
    disclaimer = blocks.CharBlock()

    class Meta:
        icon = 'text'
        label = 'Additional Disclaimer'
        help_text = 'Additional disclaimer if necessary; placed in order above standard CIGI disclaimer.'


class AdditionalFileBlock(blocks.StructBlock):
    file = DocumentChooserBlock(required=True)
    page = blocks.PageChooserBlock(required=False)
    title = blocks.CharBlock(required=False)
    description = blocks.RichTextBlock(required=False)
    image = ImageChooserBlock(required=False)

    class Meta:
        icon = 'doc-full'
        label = 'Additional File'
        help_text = 'Additional files to be used only if the theme requires them.'
        template = 'streams/additional_file_block.html'


class SeriesItemImageBlock(blocks.StructBlock):
    class PositionChoices(models.TextChoices):
        top = ('top', 'Top')
        bottom = ('bottom', 'Bottom')

    image = ImageChooserBlock(required=True)
    position = blocks.ChoiceBlock(choices=PositionChoices.choices, required=False)


class LineBreakBlock(blocks.StructBlock):
    image_map = {
        'space_series_planets': '/static/assets/space_series_planets.png',
        'space_series_stars': '/static/assets/space_series_stars.png',
        'space_series_orbit': '/static/assets/space_series_orbit.png',
        'space_series_ringed_planet': '/static/assets/space_series_ringed_planet.png',
    }
    type = blocks.ChoiceBlock(
        choices=[
            ('space_series_planets', 'Space Series Planets'),
            ('space_series_stars', 'Space Series Stars'),
            ('space_series_orbit', 'Space Series Orbit'),
            ('space_series_ringed_planet', 'Space Series Ringed Planet'),
        ],
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context['image'] = self.image_map[value.get('type')]
        context['image_class'] = value.get('type').replace('_', '-')
        return context

    class Meta:
        icon = 'horizontalrule'
        label = 'Line Break'
        template = 'streams/line_break_block.html'


class SurveyFindingsCountryBlock(blocks.StructBlock):
    country = blocks.CharBlock(required=True)
    image = ImageChooserBlock(required=True)
    file = DocumentChooserBlock(required=True)

    class Meta:
        icon = 'link'
        label = 'Survey Findings Country'
        template = 'streams/survey_findings_country_block.html'


class PersonsListBlock(blocks.StructBlock, ThemeableBlock):
    class BioSourceField(models.TextChoices):
        FULL_BIO = ('full_bio', 'Full Biography')
        SHORT_BIO = ('short_bio', 'Short Biography')

    title = blocks.CharBlock(required=False)
    bio_source_field = blocks.ChoiceBlock(
        required=False,
        choices=BioSourceField.choices,
        max_choices=1,
        verbose_name='Biography Source Field',
        help_text="Select the field from the person's page to populate their biography in this block. Default to 'Full Biography'.",
    )
    persons = blocks.StreamBlock(
        [
            ('person', blocks.PageChooserBlock(page_type='people.PersonPage', required=True)),
        ],
        required=True,
    )
    cohort = blocks.CharBlock(required=False)
    implemented_themes = [
        'ges_activity',
    ]

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(PersonsListBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'persons_list_block')

    class Meta:
        icon = 'group'
        label = 'Persons List'
        help_text = 'Add a list of person profiles.'
        template = 'streams/persons_list_block.html'


class PublicationsListBlock(blocks.StructBlock, ThemeableBlock):
    title = blocks.CharBlock(required=False)
    publication_type = blocks.PageChooserBlock(page_type='publications.PublicationTypePage', required=False, help_text='Select a publication type to automatically populate with this type of publications.')
    publications = blocks.StreamBlock(
        [
            ('publication', blocks.PageChooserBlock(page_type='publications.PublicationPage', required=True)),
        ],
        required=False,
    )
    implemented_themes = [
        'dph_page',
        'digital_finance_event',
    ]

    def get_publications_by_type(self, publication_type):
        from publications.models import PublicationPage
        return PublicationPage.objects.live().public().filter(publication_type__title=publication_type).order_by('-publishing_date')

    def get_publications_by_type_sorted(self, publication_type, by='date'):
        qs = self.get_publications_by_type(publication_type)

        if by == 'author':
            pubs = list(qs)

            def first_author_last(pub):
                first_author_rel = pub.authors.order_by('sort_order').first()
                if first_author_rel and first_author_rel.author:
                    return (first_author_rel.author.last_name or '').lower()
                return 'zzzz'

            pubs.sort(key=first_author_last)
            return pubs

        return qs

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        if value.get('publication_type'):
            pub_type = value['publication_type'].specific.title

            context['publications_by_type'] = self.get_publications_by_type(pub_type)
            context['publications_by_author'] = self.get_publications_by_type_sorted(pub_type, by='author')
        return context

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(PublicationsListBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'publications_list_block')

    class Meta:
        icon = 'doc-full'
        label = 'Publications List'
        help_text = 'Add a list of publication profiles.'
        template = 'streams/publications_list_block.html'


class AddtionalPagesBlock(blocks.StructBlock, ThemeableBlock):
    pages = blocks.StreamBlock(
        [
            ('page', blocks.PageChooserBlock(required=True)),
        ],
        required=True,
    )

    implemented_themes = [
        'dph_page',
    ]

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(AddtionalPagesBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'additional_pages_block')

    class Meta:
        icon = 'doc-full'
        label = 'Additional Pages'
        help_text = 'Add a list of additional pages.'
        template = 'streams/additional_pages_block.html'


class GESSlideBlock(blocks.StructBlock):
    label = blocks.CharBlock(required=False)
    image = ImageChooserBlock(required=True)
    caption = blocks.RichTextBlock(required=False)

    class Meta:
        icon = 'image'
        label = 'Slide'
        template = 'streams/ges_slide_block.html'


class GESHighlightsBlock(blocks.StructBlock):
    slides = blocks.StreamBlock([
        ('slide', GESSlideBlock()),
    ])
    title = blocks.CharBlock(required=False)
    description = blocks.RichTextBlock(required=False)
    pdf = DocumentChooserBlock(required=False)
    image = ImageChooserBlock(required=False)

    class Meta:
        icon = 'doc-full'
        label = 'GES Highlights'
        template = 'streams/ges_highlights_block.html'


class GESEventsBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    project = blocks.PageChooserBlock(page_type='research.ProjectPage', required=True)

    def get_context(self, value, parent_context=None):
        from events.models import EventPage
        context = super().get_context(value, parent_context)
        events = EventPage.objects.live().filter(projects=value.get('project')).order_by('publishing_date')
        context['events'] = events

        return context

    class Meta:
        icon = 'date'
        label = 'GES Events'
        template = 'streams/ges_events_block.html'


class GESSlideDeckBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    title = blocks.CharBlock(required=False)
    description = blocks.RichTextBlock(required=False)
    download = DocumentChooserBlock(required=False)
    last_updated = blocks.DateBlock(required=False)

    class Meta:
        icon = 'doc-full'
        label = 'GES Slide Deck'
        template = 'streams/ges_slide_deck_block.html'


class GESDataBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    description = blocks.RichTextBlock(required=False)
    image = ImageChooserBlock(required=False)
    download = DocumentChooserBlock(required=False)

    class Meta:
        icon = 'doc-full'
        label = 'GES Data'
        template = 'streams/ges_data_block.html'


class GESRawDataBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    description = blocks.RichTextBlock(required=False)
    download = DocumentChooserBlock(required=False)

    class Meta:
        icon = 'doc-full'
        label = 'GES Raw Data'
        template = 'streams/ges_raw_data_block.html'


class FeaturedEpisodeBlock(blocks.StructBlock):
    episode = blocks.PageChooserBlock(page_type='multimedia.MultimediaPage', required=True)

    class Meta:
        icon = 'doc-full'
        label = 'Featured Episode'
        template = 'streams/featured_episode_block.html'


class PodcastChapterBlock(blocks.StructBlock):
    text = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
    )
    timestamp = blocks.StructBlock([
        ('hours', blocks.IntegerBlock(required=True, min_value=0)),
        ('minutes', blocks.IntegerBlock(required=True, min_value=0, max_value=59)),
        ('seconds', blocks.IntegerBlock(required=True, min_value=0, max_value=59)),
    ])

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        timestamp = value.get('timestamp')
        hour = timestamp.get('hours')
        minute = timestamp.get('minutes')
        second = timestamp.get('seconds')
        timestamp_string = f"{hour}:{minute:02d}:{second:02d}"
        context['timestamp_string'] = timestamp_string

        return context

    class Meta:
        icon = 'doc-full'
        label = 'Podcast Chapter'
        template = 'streams/podcast_chapter_block.html'


class PodcastTranscriptBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    text = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
    )
    timestamp = blocks.StructBlock(
        [
            ('hours', blocks.IntegerBlock(required=False, min_value=0)),
            ('minutes', blocks.IntegerBlock(required=False, min_value=0, max_value=59)),
            ('seconds', blocks.IntegerBlock(required=False, min_value=0, max_value=59)),
        ],
        required=False,
        help_text='Enter the timestamp of the transcript if it corresponds to a specific time in the podcast.',
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        try:
            timestamp_string = f"{value.get('timestamp').get('minutes'):02d}:{value.get('timestamp').get('seconds'):02d}"
            context['timestamp_string'] = timestamp_string
        except TypeError:
            pass
        return context

    class Meta:
        icon = 'doc-full'
        label = 'Podcast Transcript'
        template = 'streams/podcast_transcript_block.html'


class Think7ChairBlock(blocks.StructBlock):
    class ChairTypeChoices(models.TextChoices):
        CHAIR = ('chair', 'Chair')
        CO_CHAIR = ('co-chair', 'Co-Chair')

    chair_type = blocks.ChoiceBlock(choices=ChairTypeChoices.choices, required=False, help_text='Chair or Co-Chair.')
    chair = blocks.PageChooserBlock(page_type='people.PersonPage', required=False, help_text='Internal profile if available.')
    url = blocks.URLBlock(required=False, help_text='URL to their external profile if internal profile is not available.')
    name = blocks.CharBlock(required=False, help_text='Chair name if internal profile is not available.')
    position = blocks.RichTextBlock(required=False, help_text='Override internal profile position.')
    image = ImageChooserBlock(required=False, help_text='Override internal profile image.')
    bio = blocks.RichTextBlock(required=False, help_text='Chair bio.')

    def clean(self, value):
        value = super().clean(value)

        word_limit = 250
        bio_content = value.get('bio', '')
        plain_text = strip_tags(bio_content.source if hasattr(bio_content, 'source') else bio_content)
        word_count = len(plain_text.split())

        if word_count > word_limit:
            raise blocks.StreamBlockValidationError({
                'bio': ValidationError(f'Bio must be less than {word_limit} words. it is currently {word_count} words.')
            })

        return value

    class Meta:
        icon = 'user'
        label = 'Taskforce Chair'
        template = 'think7/streams/chair_block.html'


class FilesBlock(blocks.StructBlock, ThemeableBlock):
    files = blocks.StreamBlock(
        [
            ('file', blocks.StructBlock(
                [
                    ('file', DocumentChooserBlock(required=True)),
                    ('title', blocks.CharBlock(required=False)),
                ],
                required=True,
            )),
        ],
        required=True,
    )

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(FilesBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'files_block')

    class Meta:
        icon = 'doc-full'
        label = 'Files'
        template = 'streams/files_block.html'


class ARSlideChooserBlock(blocks.StructBlock):
    """A block that lets editors choose slides for ordering. Used in the Annual Report SPA Page."""
    slide = blocks.PageChooserBlock(required=True, page_type=["annual_reports.AnnualReportSlidePage"])


class SPSlideChooserBlock(blocks.StructBlock):
    """A block that lets editors choose slides for ordering. Used in the Strategic Plan SPA Page."""
    slide = blocks.PageChooserBlock(required=True, page_type=["annual_reports.StrategicPlanSlidePage"])


class SPSlideFrameworkBlock(blocks.StructBlock):
    class COLOURS(models.TextChoices):
        YELLOW = ('yellow', 'Yellow')
        GREEN = ('green', 'Green')
        PINK = ('pink', 'Pink')
        BLUE = ('blue', 'Blue')
        MULTI = ('multi', 'Multi')

    title = blocks.CharBlock(required=False)
    subtitle = blocks.CharBlock(required=False)
    text_stream = blocks.StreamBlock(
        [
            ('text', blocks.RichTextBlock(required=False, features=['h2', 'bold', 'italic', 'link', 'coloured'])),
        ],
        required=False)
    colour = blocks.ChoiceBlock(choices=COLOURS.choices, required=False)


class SPSlideBoardBlock(blocks.StructBlock):
    board_members = blocks.StreamBlock([
        ('member', blocks.StructBlock([
            ('name', blocks.CharBlock(required=True)),
            ('title', blocks.CharBlock(required=True)),
        ])),
    ])


class ARSlideBoardBlock(blocks.StructBlock):
    BOARD_TYPES = [
        ('board', 'Board'),
        ('executive', 'Executive'),
    ]
    board_type = blocks.ChoiceBlock(choices=BOARD_TYPES, required=True)
    board_members = blocks.StreamBlock([
        ('member', blocks.StructBlock([
            ('name', blocks.CharBlock(required=True)),
            ('title', blocks.CharBlock(required=True)),
            ('title_line_2', blocks.CharBlock(required=False)),
            ('title_fr', blocks.CharBlock(required=True)),
            ('title_line_2_fr', blocks.CharBlock(required=False)),
            ('bio_en', blocks.RichTextBlock(required=False)),
            ('bio_fr', blocks.RichTextBlock(required=False)),
            ('page', blocks.PageChooserBlock(page_type='people.PersonPage', required=False)),
            ('image_override', ImageChooserBlock(required=False)),
            ('link_override', blocks.URLBlock(required=False, help_text='Override the link for this person')),
        ])),
    ])


class ARSlideColumnBlock(blocks.StructBlock):
    CONTENT_TYPES = [
        ('publication', 'Publication'),
        ('opinion', 'Opinion'),
        ('video', 'Video'),
        ('podcast', 'Podcast'),
        ('event', 'Event'),
        ('essay series', 'Essay Series'),
        ('media', 'Media'),
        ('news release', 'News Release'),
        ('experts', 'Experts'),
        ('subscribe', 'Subscribe'),
        ('listen', 'Listen'),
        ('explore', 'Explore'),
        ('episode', 'Episode'),
        ('research', 'Research'),
        ('survey', 'Survey'),
        ('t7', 'T7'),
        ('website', 'Website'),
    ]
    column = blocks.StreamBlock([
        ('paragraph_column', blocks.StructBlock([
            ('en', blocks.RichTextBlock(required=False, features=['bold', 'italic', 'link', 'red-line', 'chair-name'])),
            ('fr', blocks.RichTextBlock(required=False, features=['bold', 'italic', 'link', 'red-line', 'chair-name'])),
        ])),
        ('content_column', blocks.StreamBlock(
            [
                ('content', blocks.StructBlock(
                    [
                        ('type', blocks.ChoiceBlock(choices=CONTENT_TYPES, required=True)),
                        ('type_override', blocks.CharBlock(required=False, help_text='Override the content type label for this content item')),
                        ('type_override_fr', blocks.CharBlock(required=False, help_text='Override the content type label for this content item in French')),
                        ('page', blocks.PageChooserBlock(required=False)),
                        ('link_override', blocks.URLBlock(required=False, help_text='Override the link for this content item')),
                        ('title_en', blocks.RichTextBlock(required=False, help_text='Override the title for this content item')),
                        ('title_fr', blocks.RichTextBlock(required=False, help_text='Override the title for this content item')),
                    ]
                ))
            ],
            required=False
        )),
    ])


class ARFinancialsSignatureBlock(blocks.StructBlock):
    signature = ImageChooserBlock(required=False)
    signature_text = blocks.RichTextBlock(required=False, features=['bold', 'italic', 'link'])

    class Meta:
        icon = 'user'
        label = 'Signature'
        template = 'annual_reports/streams/ar_financials_signature_block.html'


class ARFinancialsAuditorReportBlock(blocks.StructBlock):
    title_en = blocks.CharBlock(required=False)
    title_fr = blocks.CharBlock(required=False)
    columns = blocks.StreamBlock([
        ('column', blocks.StructBlock([
            ('en', blocks.StreamBlock([
                ('paragraph', blocks.RichTextBlock(required=False, features=['bold', 'italic', 'link', 'h4'])),
                ('signature', ARFinancialsSignatureBlock()),
            ])),
            ('fr', blocks.StreamBlock([
                ('paragraph', blocks.RichTextBlock(required=False, features=['bold', 'italic', 'link', 'h4'])),
                ('signature', ARFinancialsSignatureBlock()),
            ])),
        ]))
    ])


class ARFinancialPositionBlock(blocks.StructBlock):
    title_en = blocks.CharBlock(required=False)
    title_fr = blocks.CharBlock(required=False)
    description_en = blocks.RichTextBlock(required=False, features=['bold', 'italic', 'link', 'ol', 'ul'])
    description_fr = blocks.RichTextBlock(required=False, features=['bold', 'italic', 'link', 'ol', 'ul'])

    amounts = blocks.StructBlock([
        ('year_current', blocks.StructBlock([
            ('year_label', blocks.CharBlock(required=False)),
            ('cash_and_cash_equivalents', (blocks.CharBlock(required=False))),
            ('portfolio_investments', (blocks.CharBlock(required=False))),
            ('amounts_receivable', (blocks.CharBlock(required=False))),
            ('prepaid_expenses', (blocks.CharBlock(required=False))),
            ('current_assets_subtotal', (blocks.CharBlock(required=False))),
            ('property_and_equipment', (blocks.CharBlock(required=False))),
            ('lease_inducement', (blocks.CharBlock(required=False))),
            ('other_assets_subtotal', (blocks.CharBlock(required=False))),
            ('total_assets', (blocks.CharBlock(required=False))),
            ('accounts_payable_and_accrued_liabilities', (blocks.CharBlock(required=False))),
            ('deferred_revenue', (blocks.CharBlock(required=False))),
            ('total_liabilities', (blocks.CharBlock(required=False))),
            ('invested_in_capital_assets', (blocks.CharBlock(required=False))),
            ('externally_restricted', (blocks.CharBlock(required=False))),
            ('internally_restricted', (blocks.CharBlock(required=False))),
            ('unrestricted', (blocks.CharBlock(required=False))),
            ('total_fund_balances', (blocks.CharBlock(required=False))),
            ('total_liabilities_and_fund_balances', (blocks.CharBlock(required=False))),
        ])),
        ('year_previous', blocks.StructBlock([
            ('year_label', blocks.CharBlock(required=False)),
            ('cash_and_cash_equivalents', (blocks.CharBlock(required=False))),
            ('portfolio_investments', (blocks.CharBlock(required=False))),
            ('amounts_receivable', (blocks.CharBlock(required=False))),
            ('prepaid_expenses', (blocks.CharBlock(required=False))),
            ('current_assets_subtotal', (blocks.CharBlock(required=False))),
            ('property_and_equipment', (blocks.CharBlock(required=False))),
            ('lease_inducement', (blocks.CharBlock(required=False))),
            ('other_assets_subtotal', (blocks.CharBlock(required=False))),
            ('total_assets', (blocks.CharBlock(required=False))),
            ('accounts_payable_and_accrued_liabilities', (blocks.CharBlock(required=False))),
            ('deferred_revenue', (blocks.CharBlock(required=False))),
            ('total_liabilities', (blocks.CharBlock(required=False))),
            ('invested_in_capital_assets', (blocks.CharBlock(required=False))),
            ('externally_restricted', (blocks.CharBlock(required=False))),
            ('internally_restricted', (blocks.CharBlock(required=False))),
            ('unrestricted', (blocks.CharBlock(required=False))),
            ('total_fund_balances', (blocks.CharBlock(required=False))),
            ('total_liabilities_and_fund_balances', (blocks.CharBlock(required=False))),
        ]))
    ])

    class Meta:
        icon = 'doc-full'
        label = 'Financial Position'
        template = 'annual_reports/streams/ar_financial_position_block.html'


class ARFundBalancesBlock(blocks.StructBlock):
    title_en = blocks.CharBlock(required=False)
    title_fr = blocks.CharBlock(required=False)
    description_en = blocks.RichTextBlock(required=False, features=['bold', 'italic', 'link', 'ol', 'ul'])
    description_fr = blocks.RichTextBlock(required=False, features=['bold', 'italic', 'link', 'ol', 'ul'])

    amounts = blocks.StructBlock([
        ('year_current', blocks.StructBlock([
            ('year_label', blocks.CharBlock(required=False)),
            ('realized_investment_income', (blocks.CharBlock(required=False))),
            ('unrealized_investment_gains', (blocks.CharBlock(required=False))),
            ('other', (blocks.CharBlock(required=False))),
            ('government_and_other_grants', (blocks.CharBlock(required=False))),
            ('total_revenue', (blocks.CharBlock(required=False))),
            ('research_and_conferences', (blocks.CharBlock(required=False))),
            ('amortization', (blocks.CharBlock(required=False))),
            ('administration', (blocks.CharBlock(required=False))),
            ('facilities', (blocks.CharBlock(required=False))),
            ('technical_support', (blocks.CharBlock(required=False))),
            ('total_expenses', (blocks.CharBlock(required=False))),
            ('excess_of_expenses_over_revenue', (blocks.CharBlock(required=False))),
            ('fund_balances_beginning_of_year', (blocks.CharBlock(required=False))),
            ('fund_balances_end_of_year', (blocks.CharBlock(required=False))),
        ])),
        ('year_previous', blocks.StructBlock([
            ('year_label', blocks.CharBlock(required=False)),
            ('realized_investment_income', (blocks.CharBlock(required=False))),
            ('unrealized_investment_gains', (blocks.CharBlock(required=False))),
            ('other', (blocks.CharBlock(required=False))),
            ('government_and_other_grants', (blocks.CharBlock(required=False))),
            ('total_revenue', (blocks.CharBlock(required=False))),
            ('research_and_conferences', (blocks.CharBlock(required=False))),
            ('amortization', (blocks.CharBlock(required=False))),
            ('administration', (blocks.CharBlock(required=False))),
            ('facilities', (blocks.CharBlock(required=False))),
            ('technical_support', (blocks.CharBlock(required=False))),
            ('total_expenses', (blocks.CharBlock(required=False))),
            ('excess_of_expenses_over_revenue', (blocks.CharBlock(required=False))),
            ('fund_balances_beginning_of_year', (blocks.CharBlock(required=False))),
            ('fund_balances_end_of_year', (blocks.CharBlock(required=False))),
        ]))
    ])

    class Meta:
        icon = 'doc-full'
        label = 'Fund Balances'
        template = 'annual_reports/streams/ar_fund_balances_block.html'


class AROutputsBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)

    outputs = blocks.StreamBlock([
        ('output', blocks.StructBlock([
            ('page', blocks.PageChooserBlock(required=False)),
            ('title_override', blocks.CharBlock(required=False)),
            ('link_override', blocks.URLBlock(required=False, help_text='Override the link for this content item')),
            ('description_override', blocks.RichTextBlock(required=False, features=['bold', 'italic', 'link'])),
            ('image_override', ImageChooserBlock(required=False)),
            ('type_override', blocks.CharBlock(required=False, help_text='Override the type of output (e.g., Publication, Opinion, Video, Podcast, Event).'))
        ])),
    ])


class ResourceBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    description = blocks.RichTextBlock(required=False)
    file = DocumentChooserBlock(required=False)
    cta_link = blocks.URLBlock(required=False)
    cta_text = blocks.CharBlock(required=False)
    image = ImageChooserBlock(required=False)

    class Meta:
        icon = 'link'
        label = 'Resource'
        template = 'streams/resource_block.html'


class T7CommuniqueBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock(page_type='publications.T7PublicationPage', required=False)
    description = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
    )
    image_override = ImageChooserBlock(required=False)
    title_override = blocks.CharBlock(required=False)

    class Meta:
        icon = 'doc-full'
        label = 'T7 Communique'
        template = 'streams/t7_communique_block.html'


class SovereignCanadaRationaleBlock(blocks.StructBlock):
    documents = blocks.StreamBlock(
        [
            ('document', blocks.StructBlock(
                [
                    ('file', DocumentChooserBlock(required=True)),
                    ('title', blocks.CharBlock(required=False)),
                    ('size', blocks.ChoiceBlock(
                        choices=[
                            ('small', 'Small'),
                            ('large', 'Large'),
                        ],
                        default='large',
                    )),
                ],
                required=True,
            )),
        ],
        required=True,
    )

    class Meta:
        icon = 'doc-full'
        label = 'Sovereign Canada Rationale'
        template = 'streams/sovereign_canada_rationale_block.html'


class SovereignCanadaDashboardBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    categories = blocks.StreamBlock(
        [
            ('category', blocks.StructBlock(
                [
                    ('title', blocks.CharBlock(required=True, help_text='Title of the category.')),
                    ('files', blocks.StreamBlock(
                        [
                            ('file', DocumentChooserBlock(required=True, help_text='File to be displayed in the category.')),
                        ],
                        required=False,
                    ))
                ],
                required=True,
            )),
        ],
        required=True,
    )

    class Meta:
        icon = 'doc-full'
        label = 'Sovereign Canada Dashboard'
        template = 'streams/sovereign_canada_dashboard_block.html'


class AbstractSubmissionBlock(blocks.StructBlock):
    # Renders a block that contains a form for submitting abstracts.
    class Meta:
        icon = 'form'
        label = 'Abstract Submission Form'
        template = 'streams/abstract_submission_form_block.html'


class CollapsibleParagraphBlock(blocks.StructBlock, ThemeableBlock):
    """Standard text paragraph that is collapsible."""

    collapsed = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text="If checked, the paragraph will be collapsed by default.",
    )
    title = blocks.RichTextBlock(
        required=False,
        features=[
            'bold',
            'italic',
            'link',
        ],
        help_text="Optional title for the collapsible paragraph.",
    )
    title_type = blocks.ChoiceBlock(
        choices=[
            ('h2', 'H2'),
            ('h3', 'H3'),
            ('h4', 'H4'),
        ],
        default='h2',
        help_text="Select the heading type for the title.",
    )
    paragraph = blocks.RichTextBlock(
        required=True,
        features=[
            'bold',
            'dropcap',
            'endofarticle',
            'paragraph_heading',
            'h2',
            'h3',
            'h4',
            'hr',
            'image',
            'italic',
            'underline',
            'link',
            'ol',
            'subscript',
            'superscript',
            'ul',
            'anchor',
            'rtl',
        ],
    )

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(CollapsibleParagraphBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'collapsible_paragraph_block')

    class Meta:
        icon = 'edit'
        label = 'Collapsible Paragraph'
        template = 'streams/collapsible_paragraph_block.html'


class FloatedBioBlock(blocks.StructBlock):
    """A block for displaying a floated bio with an image and text."""

    title = blocks.CharBlock(
        required=True,
        help_text="Title of the bio.",
    )
    image = ImageChooserBlock(required=True, help_text="Image to be displayed alongside the bio.")
    short_text = blocks.RichTextBlock(
        required=True,
        features=[
            'bold',
            'italic',
            'link',
        ],
        help_text="Short text content of the bio.",
    )
    text = blocks.RichTextBlock(
        required=True,
        features=[
            'bold',
            'italic',
            'link',
        ],
        help_text="Text content of the bio.",
    )

    class Meta:
        icon = 'user'
        label = 'Floated Bio'
        template = 'streams/floated_bio_block.html'


class CAIAIObjectivesBlock(blocks.StructBlock):
    """A block for displaying the objectives of the CAI AI."""

    objectives = blocks.RichTextBlock(
        required=True,
        features=[
            'h2',
            'h3',
            'ul',
            'bold',
            'italic',
            'link',
        ],
        help_text="Text content of the CAI AI Objectives.",
    )

    class Meta:
        icon = 'doc-full'
        label = 'CAI AI Objectives'
        template = 'streams/caiai_objectives_block.html'


class NewsletterSubscriptionBlock(blocks.StructBlock, ThemeableBlock):
    """A block for displaying a newsletter subscription form."""

    scheme = blocks.ChoiceBlock(
        choices=[('red', 'Red (default)'), ('green', 'Green (DPH)')],
        default='red',
        required=False,
        help_text='Colour wash of the band. Green is the Digital Policy Hub '
                  'treatment (DPH About design).',
    )

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(NewsletterSubscriptionBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'newsletter_subscription_block')

    class Meta:
        icon = 'mail'
        label = 'Newsletter Subscription'
        template = 'streams/newsletter_subscription_block.html'


class NewsletterSignupCTABlock(blocks.StructBlock):
    """The full newsletter sign-up panel (mod library CTA/15, 1360:106698): a
    red panel — duotone photo under the brand-red wash — with the ruled heading
    top-left, serif text bottom-left, and the first/last/email sign-up form
    bottom-right (posting the same /subscribe/ prefill hand-off as the slim
    NewsletterSubscriptionBlock band)."""

    heading = blocks.CharBlock(required=False, default='Subscribe to Our Newsletter')
    text = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'], required=False,
        help_text='Serif paragraph in the lower-left of the panel.',
    )
    image = ImageChooserBlock(
        required=False,
        help_text='Background photo under the red wash; the bundled texture is used when empty.',
    )
    # The red panel never changes; the surface colours the band AROUND it so
    # the section flows with the module above (QA regroup / BugHerd #111).
    surface = blocks.ChoiceBlock(
        # Green joins light/dark for the DPH hub, whose bands are green
        # (BugHerd #171).
        choices=[('light', 'Light'), ('dark', 'Dark'), ('green', 'Green')],
        default='light', max_length=8,
        help_text='Match the surface of the module above so the band flows with it.',
    )

    class Meta:
        icon = 'mail'
        label = 'Newsletter Sign-up CTA'
        template = 'streams/newsletter_signup_cta_block.html'


class DotDividerBlock(blocks.StaticBlock):
    """A decorative row of five coloured dots."""

    class Meta:
        icon = 'horizontalrule'
        label = 'Dot Divider'
        template = 'streams/dot_divider_block.html'


class SectionHeadingBlock(blocks.StructBlock):
    """A section heading with an optional custom nav label."""

    heading = blocks.CharBlock(required=True)
    nav_label = blocks.CharBlock(
        required=False,
        help_text='Optional shorter label shown in the sidebar navigation. Defaults to the heading text if left blank.',
    )

    class Meta:
        icon = 'title'
        label = 'Section Heading'
        template = 'streams/section_heading_block.html'


class BorderedContentBlock(blocks.StructBlock):
    """A richtext section wrapped in a 1px black border box."""

    content = blocks.RichTextBlock(
        required=True,
        features=[
            'bold',
            'h2',
            'h3',
            'h4',
            'italic',
            'underline',
            'link',
            'ol',
            'ul',
            'subscript',
            'superscript',
            'anchor',
        ],
    )

    class Meta:
        icon = 'form'
        label = 'Bordered Content'
        template = 'streams/bordered_content_block.html'


class CollapsibleParagraphContentStreamBlock(blocks.StreamBlock):
    """Content stream used inside CollapsibleParagraphBlockV2."""

    richtext = blocks.RichTextBlock(
        required=False,
        features=[
            'bold',
            'dropcap',
            'endofarticle',
            'paragraph_heading',
            'h2',
            'h3',
            'h4',
            'hr',
            'image',
            'italic',
            'underline',
            'link',
            'ol',
            'subscript',
            'superscript',
            'ul',
            'anchor',
            'rtl',
        ],
        label='Rich Text',
    )
    bordered_content = BorderedContentBlock()

    class Meta:
        block_counts = {'richtext': {'min_num': 1}}


class CollapsibleParagraphBlockV2(blocks.StructBlock):
    """Collapsible paragraph block whose content is a stream of richtext and
    bordered sections. Use this for new content; existing pages continue to
    use CollapsibleParagraphBlock unchanged."""

    collapsed = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text='If checked, the paragraph will be collapsed by default.',
    )
    title = blocks.RichTextBlock(
        required=False,
        features=['bold', 'italic', 'link'],
        help_text='Optional title for the collapsible paragraph.',
    )
    title_type = blocks.ChoiceBlock(
        choices=[('h2', 'H2'), ('h3', 'H3'), ('h4', 'H4')],
        default='h2',
        help_text='Select the heading type for the title.',
    )
    content = CollapsibleParagraphContentStreamBlock()

    class Meta:
        icon = 'edit'
        label = 'Collapsible Paragraph V2'
        template = 'streams/collapsible_paragraph_block_v2.html'


class PromotionBlockStreamBlock(blocks.StructBlock):
    block = SnippetChooserBlock('promotions.PromotionBlock')

    class Meta:
        icon = 'pick'
        label = 'Promotion Block'
        template = 'streams/promotion_block_stream_block.html'


def _slugify_label(label, used):
    """Derive a stable, unique tab slug from a tab label (decision D5). Falls back
    to a positional slug when a label slugifies to empty / collides."""
    from django.utils.text import slugify
    base = slugify(label or '') or 'tab'
    slug = base
    i = 2
    while slug in used:
        slug = '%s-%d' % (base, i)
        i += 1
    used.add(slug)
    return slug


class FacetedListingBlock(ConditionalFieldsMixin, blocks.StructBlock):
    """Placeable faceted-listing module — the shared ``.ds-router`` filter + cards
    + pager shell exposed as a StreamField block (net-new #2). One reusable module
    across every archive listing: the author supplies the **card type**, the
    **scope** (program / publication subtype / person type), which **facets** to
    show, and a stable per-instance **prefix** so multiple listings on one page
    never collide on the querystring (decision D2).

    Filtering, paging and the AJAX partial-swap are handled by
    ``core.faceted_listing`` + the shared ``router.js``; this block only carries
    config. Set ``show_filters`` off for the no-filter variant (DPH Speakers grid).
    """

    CARD_TYPES = [
        ('resource', 'Resource (program-scoped)'),
        ('publication', 'Publication (e.g. Working Papers)'),
        ('person', 'Person (Cohort / Speakers)'),
        ('staff', 'Staff directory'),
        ('expert', 'Expert'),
        ('news', 'News / In the News / Opinion'),
        ('opinion', 'Opinion archive (Op-Eds / Opinion / Essays / Interviews)'),
        ('episode_row', 'Podcast episode'),
        ('event', 'Event'),
        ('report', 'Annual report'),
    ]
    PERSON_TYPES = [
        ('dph_fellow', 'Digital Policy Hub Fellow'),
        # DPH Speaker (BugHerd #177): the hub's own tag. 'speaker' below is the
        # legacy Drupal event-speaker population and stays for the archives.
        ('dph_speaker', 'DPH Speaker'),
        ('speaker', 'Speaker'),
        ('research_fellow', 'Research Fellow'),
        ('expert', 'Expert'),
        ('management_board', 'Senior Management & Board'),
        ('management_team', 'Management Team'),
        ('board', 'Board'),
        ('staff', 'Staff'),
    ]
    PUBLICATION_TYPES = [
        ('working-paper', 'Working Paper'),
        ('policy-briefs', 'Policy Briefs'),
        ('cigi-papers', 'CIGI Papers'),
        ('special-reports', 'Special Reports'),
        ('books', 'Books'),
    ]
    # No A–Z: the search box already filters the same list from one input, so an
    # alphabet in the filter drawer earned nothing (Evan, BugHerd #231).
    FACETS = [
        ('topic', 'Topic'),
        ('type', 'Type / Role'),
        ('experts', 'Experts (news)'),
        ('author', 'Author: CIGI Experts / Contributors (opinion)'),
        ('year', 'Year'),
        ('season', 'Season (podcast)'),
        ('location', 'Location (events)'),
        ('date', 'Date calendar (events)'),
    ]

    # Surface/accent lead the form, like every other DS module (BugHerd #94).
    # Defaults inherit the page so existing placements are unchanged.
    surface = blocks.ChoiceBlock(choices=SurfaceMixin.Surface.choices, default=SurfaceMixin.Surface.INHERIT, required=False)
    accent = blocks.ChoiceBlock(choices=SurfaceMixin.Accent.choices, required=False)
    heading = blocks.CharBlock(required=False, help_text='Optional section heading above the listing.')
    intro = blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False)
    card_type = blocks.ChoiceBlock(choices=CARD_TYPES, default='resource')
    prefix = blocks.CharBlock(
        required=False, max_length=24,
        help_text='Short, unique id for this listing\'s URL params (letters/numbers, '
                  'e.g. "papers"). Auto-generated if blank. Keep distinct from other '
                  'listings on the same page.')

    # Scope controls (used per card type).
    program_source = blocks.ChoiceBlock(
        choices=[
            ('auto', 'Auto (the program or theme page this is placed on)'),
            ('manual', 'Pick a program'),
            # The Archive page (Evan, 2026-09-10): every live content page that
            # carries no current-IA program — the tail the program routers
            # can't reach. Includes the news types.
            ('none', 'Archive — content with no program'),
        ],
        default='auto', required=False, help_text='Resource card type only.')
    program = blocks.PageChooserBlock(page_type='research.ProjectPage', required=False)
    # Per-instance content-type toggles (QA regroup 17:46/22:05): the resource
    # listing includes only these types, and its filters auto-build from them.
    content_types = blocks.MultipleChoiceBlock(
        choices=[
            ('opinion', 'Opinions'),
            ('publication', 'Publications'),
            ('multimedia', 'Multimedia'),
            ('event', 'Events'),
        ],
        required=False,
        help_text='Resource card type only: the content types this listing includes. '
                  'Filters build automatically from these. Empty = all types.')
    publication_type = blocks.ChoiceBlock(
        choices=PUBLICATION_TYPES, default='working-paper', required=False,
        help_text='Publication card type only.')
    person_type = blocks.ChoiceBlock(
        choices=PERSON_TYPES, default='dph_fellow', required=False,
        help_text='Person card type only.')
    series_source = blocks.ChoiceBlock(
        choices=[('auto', 'Auto (the podcast series this is placed on)'), ('manual', 'Pick a series')],
        default='auto', required=False, help_text='Podcast episode card type only.')
    series = blocks.PageChooserBlock(
        page_type='multimedia.MultimediaSeriesPage', required=False,
        help_text='Podcast episode card type only (manual scope).')
    news_prefilter = blocks.ChoiceBlock(
        choices=[
            ('', 'No prefilter (all three news types)'),
            ('news-release', 'CIGI News'),
            ('cigi-in-the-news', 'CIGI in the News'),
            ('op-eds', 'Opinion-Eds'),
        ],
        required=False, default='',
        help_text='News card type only: the archive lands with this type already '
                  'selected (CIGI News vs CIGI in the News archive).')

    # Facet controls.
    show_filters = blocks.BooleanBlock(
        required=False, default=True,
        help_text='Off = plain card grid + pager, no filter sidebar (e.g. Speakers).')
    show_search = blocks.BooleanBlock(required=False, default=True, help_text='Show the search input.')
    facets = blocks.MultipleChoiceBlock(
        choices=FACETS, required=False,
        help_text='Which facet groups to offer. The list narrows to the groups '
                  'the chosen card type can build. Resource listings ignore this '
                  'field — their filters build from the content types.')
    empty_text = blocks.CharBlock(required=False, help_text='Message shown when nothing matches.')

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        request = (parent_context or {}).get('request')
        page = (parent_context or {}).get('page')
        # Inactive tab panels render a lazy placeholder; the active panel (or a
        # listing placed directly on a page body) renders fully (decisions D3/D1).
        tab_active = (parent_context or {}).get('tab_active', True)
        # The owning tab's slug (threaded by the composable Tabs template) — used
        # for the no-JS GET form's hidden `tab` field so submitting/filtering keeps
        # the active tab. Independent of the request URL, so inactive (lazy) panels
        # still carry the right value.
        tab_slug = (parent_context or {}).get('tab_slug')
        from core.faceted_listing import build_listing_context
        if request is not None:
            context.update(build_listing_context(
                request, value, page=page, lazy=not tab_active, tab_slug=tab_slug))
        # Distinct names (not `self.*`): the same template is included directly
        # by page templates (series All Episodes, expert single), where `self`
        # is the PAGE — those placements must keep the inherit default.
        context['router_surface'] = value.get('surface') or 'inherit'
        context['router_accent'] = value.get('accent') or ''
        return context

    class Meta:
        icon = 'search'
        label = 'Faceted Listing'
        template = 'streams/faceted_listing_block.html'


def composable_tab_modules():
    """The DS module set an author can place inside a composable tab panel — the
    dynamic/content modules plus the placeable faceted-listing module. Defined as a
    function so the Tabs block can reuse it for every consumer."""
    return [
        ('faceted_listing', FacetedListingBlock()),
        ('program_spotlight', ProgramSpotlightBlock()),
        ('program_grid', ProgramGridBlock()),
        ('programs_carousel', ProgramsCarouselBlock()),
        ('experts_grid', ExpertsGridBlock()),
        ('experts_carousel', ExpertsCarouselBlock()),
        ('resource_carousel', ResourceCarouselBlock()),
        ('resource_bento', ResourceBentoBlock()),
        ('events_carousel', EventsCarouselBlock()),
        ('news_grid', NewsGridBlock()),
        ('trending_issues', TrendingIssuesBlock()),
        ('jobs_list', JobsListBlock()),
        ('text_columns', TextColumnsBlock()),
        ('stats', StatsBlock()),
        ('image_text', ImageTextBlock()),
        ('cta_image', CTAImageBlock()),
        ('banner', BannerBlock()),
        ('text_card_grid', TextCardGridBlock()),
        ('video_carousel', VideoCarouselBlock()),
        ('video_text', VideoTextBlock()),
        ('gallery_text', GalleryTextBlock()),
        ('supporting_materials', SupportingMaterialsBlock()),
        ('accordion_module', AccordionModuleBlock()),
        # Same key as the page-level body block, so a form authored on a page
        # moves into a tab panel unchanged (Tia, BugHerd #163 — the venue form
        # was placeable on the page but not inside a tab).
        ('form', FormSectionBlock()),
        ('general_inquiry_form', GeneralInquiryBlock()),
        ('newsletter_subscription', NewsletterSubscriptionBlock()),
        ('newsletter_signup_cta', NewsletterSignupCTABlock()),
        ('split_hero', SplitHeroBlock()),
        ('primary_hero', PrimaryHeroBlock()),
        ('horizontal_tabs', HorizontalTabsBlock()),
        ('paragraph', ParagraphBlock()),
        ('image', ImageBlock()),
    ]


class ComposableTabBlock(blocks.StructBlock):
    """One tab of a composable Tabs block: a label and a nested StreamField of DS
    modules (decision D5). Distinct from the rich-text ``HeroTabBlock``."""

    label = blocks.CharBlock(required=True)
    content = blocks.StreamBlock(composable_tab_modules(), required=False)

    class Meta:
        icon = 'doc-full'
        label = 'Tab'


class ComposableTabsBlock(blocks.StructBlock, ThemeableBlock):
    """Author-composable tabbed section (decision D5): a tab strip + one panel per
    tab, each panel holding an arbitrary StreamField of DS modules (including the
    faceted-listing module). Replaces both the rich-text-only Horizontal Tabs and
    bespoke per-page tabbed templates. Tab state lives in the URL (``?tab=<slug>``,
    slug derived from the label); panels lazy-load inactive routers (D1/D3).
    """

    heading = blocks.CharBlock(required=False, help_text='Optional accessible label for the tab group.')
    tabs = blocks.ListBlock(ComposableTabBlock())

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        request = (parent_context or {}).get('request')
        active_param = request.GET.get('tab') if request else None

        used = set()
        tabs = []
        for tab in value.get('tabs') or []:
            slug = _slugify_label(tab.get('label'), used)
            tabs.append({'label': tab.get('label'), 'slug': slug, 'content': tab.get('content')})

        active_index = 0
        if active_param:
            for i, t in enumerate(tabs):
                if t['slug'] == active_param:
                    active_index = i
                    break
        for i, t in enumerate(tabs):
            t['active'] = (i == active_index)

        context['tabs'] = tabs
        context['group_id'] = 'ds-tabs-%s' % uuid.uuid4().hex[:8]
        return context

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(ComposableTabsBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'composable_tabs_block')

    class Meta:
        icon = 'list-ul'
        label = 'Tabs (composable)'
        template = 'streams/composable_tabs_block.html'




# --- Authoring conditionals ---------------------------------------------------
# One table for every ConditionalFieldsMixin block: which fields each value of
# the controlling child reveals (see the mixin docstring; applied editor-side
# by ds_block_conditionals.js). The shared population trio is mode: auto →
# count / manual → the picker list; program modules add program_source →
# program; carousels reveal autoplay_speed only when autoplay is on.

_POPULATE_ITEMS = {'mode': {'auto': ['count'], 'manual': ['items']}}
_POPULATE_EXPERTS = {'mode': {'auto': ['count'], 'manual': ['experts']}}
_PROGRAM_SOURCE = {'program_source': {'manual': ['program', 'programs'], 'auto': [], 'none': []}}

ProgramGridBlock.CONDITIONAL_FIELDS = {**_PROGRAM_SOURCE, **_POPULATE_ITEMS}
ProgramsCarouselBlock.CONDITIONAL_FIELDS = {**_PROGRAM_SOURCE, **_POPULATE_ITEMS}
ExpertsGridBlock.CONDITIONAL_FIELDS = _POPULATE_EXPERTS
ExpertsCarouselBlock.CONDITIONAL_FIELDS = _POPULATE_EXPERTS
ResourceCarouselBlock.CONDITIONAL_FIELDS = _POPULATE_ITEMS
ResourceBentoBlock.CONDITIONAL_FIELDS = _POPULATE_ITEMS
EventsCarouselBlock.CONDITIONAL_FIELDS = _POPULATE_ITEMS
NewsCarouselBlock.CONDITIONAL_FIELDS = _POPULATE_ITEMS
NewsGridBlock.CONDITIONAL_FIELDS = _POPULATE_ITEMS
JobsListBlock.CONDITIONAL_FIELDS = _POPULATE_ITEMS
TrendingIssuesBlock.CONDITIONAL_FIELDS = {'mode': {'manual': ['item'], 'auto': []}}
# Faceted Listing: each card type reveals only its own scope controls; resource
# listings swap the manual facet picker for content-type toggles (QA regroup
# 17:46/18:08 — filters auto-build from the enabled types).
FacetedListingBlock.CONDITIONAL_FIELDS = {'card_type': {
    'resource': ['program_source', 'program', 'content_types'],
    'resource-visual': ['program_source', 'program', 'content_types'],
    'publication': ['publication_type', 'facets'],
    'person': ['person_type', 'facets'],
    'staff': ['facets'],
    'expert': ['facets'],
    'news': ['news_prefilter', 'facets'],
    'opinion': ['facets'],
    'episode_row': ['series_source', 'series', 'facets'],
    'event': ['facets'],
    'report': ['facets'],
}}
telepath_register(FacetedListingBlockAdapter(), FacetedListingBlock)

VideoCarouselBlock.CONDITIONAL_FIELDS = {'autoplay': {'true': ['autoplay_speed'], 'false': []}}
SupportingMaterialsBlock.CONDITIONAL_FIELDS = {'autoplay': {'true': ['autoplay_speed'], 'false': []}}
