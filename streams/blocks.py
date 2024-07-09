
from bs4 import BeautifulSoup
from django.conf import settings
from django.db import models
from django.forms.utils import flatatt
from django.utils import timezone
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
import wagtail.rich_text as rich_text
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.blocks import AbstractMediaChooserBlock
import pytz


class ThemeableBlock:
    implemented_themes = []

    def get_theme_dir(self, theme_name):
        return theme_name.lower().replace(' ', '_').replace("-", '_')

    def get_page_type_dir(self, verbose_name):
        return verbose_name.lower().replace(' ', '_')

    def get_theme_template(self, standard_template, context, template_name):
        if (
            context and
            context['page'] and
            hasattr(context['page'], '_meta') and
            hasattr(context['page']._meta, 'verbose_name') and
            hasattr(context['page'], 'theme') and
            context['page'].theme and
            f'{self.get_theme_dir(context["page"].theme.name)}_{self.get_page_type_dir(context["page"]._meta.verbose_name)}' in self.implemented_themes
        ):
            return f'themes/{self.get_theme_dir(context["page"].theme.name)}/streams/{self.get_page_type_dir(context["page"]._meta.verbose_name)}_{template_name}.html'
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

    def get_template(self, value, context, *args, **kwargs):
        standard_template = super(AccordionBlock, self).get_template(value, context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'accordion_block')

    class Meta:
        icon = 'edit'
        label = 'Accordion'
        template = 'streams/accordion_block.html'


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
        'indigenous_lands_series_opinion_series'
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

    def render(self, value, context=None):
        return """
        <div class="container table-block">
        <div class="row d-block">
        <div class="col col-md-10 offset-md-1 col-lg-8 offset-lg-2">
        {super_template}
        </div>
        </div>
        </div>
        """.format(super_template=super(TableStreamBlock, self).render(value, context))

    class Meta:
        icon = 'form'
        label = 'Table'


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


class TooltipBlock(blocks.StructBlock):
    """Tooltip block"""

    anchor = blocks.CharBlock(required=True)
    text = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=True,
    )
    name = blocks.CharBlock(required=False)
    title = blocks.CharBlock(required=False)
    image = ImageChooserBlock(required=False)

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


class PublicastionsListBlock(blocks.StructBlock):
    publication_type = blocks.PageChooserBlock(page_type='publications.PublicationTypePage', required=False, help_text='Select a publication type to automatically populate with this type of publications.')
    publications = blocks.StreamBlock(
        [
            ('publication', blocks.PageChooserBlock(page_type='publications.PublicationPage', required=True)),
        ],
        required=False,
    )

    def get_publications_by_type(self, publication_type):
        from publications.models import PublicationPage
        return PublicationPage.objects.live().public().filter(publication_type__title=publication_type).order_by('-publishing_date')

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        if value.get('publication_type'):
            context['publications_by_type'] = self.get_publications_by_type(value.get('publication_type').specific.title)
        return context

    class Meta:
        icon = 'doc-full'
        label = 'Publications List'
        help_text = 'Add a list of publication profiles.'
        template = 'streams/publications_list_block.html'


class AddtionalPagesBlock(blocks.StructBlock):
    pages = blocks.StreamBlock(
        [
            ('page', blocks.PageChooserBlock(required=True)),
        ],
        required=True,
    )

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
