
from bs4 import BeautifulSoup, SoupStrainer
from django.conf import settings
from django.db import models
from django.forms.utils import flatatt
from django.utils import timezone
from django.utils.html import format_html, format_html_join
from distutils.log import error
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtailmedia.blocks import AbstractMediaChooserBlock
import pytz
import os
import re
import traceback


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

    def get_template(self, context, *args, **kwargs):
        standard_template = super(AccordionBlock, self).get_template(context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'accordion_block')

    class Meta:
        icon = 'edit'
        label = 'Accordion'
        template = 'streams/accordion_block.html'


class PersonBlock(blocks.PageChooserBlock, ThemeableBlock):

    def get_template(self, context, *args, **kwargs):
        standard_template = super(PersonBlock, self).get_template(context, *args, **kwargs)
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

    def get_template(self, context, *args, **kwargs):
        standard_template = super(AutoPlayVideoBlock, self).get_template(context, *args, **kwargs)
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

    def get_template(self, context, *args, **kwargs):
        standard_template = super(BlockQuoteBlock, self).get_template(context, *args, **kwargs)
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

    def get_template(self, context, *args, **kwargs):
        standard_template = super(BookPurchaseLinkBlock, self).get_template(context, *args, **kwargs)
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

    def get_template(self, context, *args, **kwargs):
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

    def get_template(self, context, *args, **kwargs):
        standard_template = super(CTABlock, self).get_template(context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'cta_block')

    class Meta:
        icon = 'view'
        label = 'Call to Action'


class EditorBlock(blocks.PageChooserBlock, ThemeableBlock):

    def get_template(self, context, *args, **kwargs):
        standard_template = super(EditorBlock, self).get_template(context, *args, **kwargs)
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

    def get_template(self, context, *args, **kwargs):
        standard_template = super(EmbeddedMultimediaBlock, self).get_template(context, *args, **kwargs)
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

    def get_template(self, context, *args, **kwargs):
        standard_template = super(EmbeddedVideoBlock, self).get_template(context, *args, **kwargs)
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

    def get_template(self, context, *args, **kwargs):
        standard_template = super(ExternalQuoteBlock, self).get_template(context, *args, **kwargs)
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

    def get_template(self, context, *args, **kwargs):
        standard_template = super(ExternalVideoBlock, self).get_template(context, *args, **kwargs)
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

    def get_template(self, context, *args, **kwargs):
        standard_template = super(ExtractBlock, self).get_template(context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'extract_block')

    class Meta:
        icon = 'edit'
        label = 'Extract'
        template = 'streams/extract_block.html'


class ImageBlock(blocks.StructBlock, ThemeableBlock):
    """Image"""

    image = ImageChooserBlock(required=True)
    hide_image_caption = blocks.BooleanBlock(required=False)

    implemented_themes = [
        'cyber_series_opinion',
        'data_series_opinion',
        'longform_2_opinion',
        'space_series_opinion',
    ]

    def get_template(self, context, *args, **kwargs):
        standard_template = super(ImageBlock, self).get_template(context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'image_block')

    class Meta:
        icon = 'image'
        label = 'Image'
        template = 'streams/image_block.html'


class ImageFullWidthBlock(blocks.StructBlock, ThemeableBlock):
    """Full width image"""

    image = ImageChooserBlock(required=True)
    hide_image_caption = blocks.BooleanBlock(required=False)

    def get_template(self, context, *args, **kwargs):
        standard_template = super(ImageFullWidthBlock, self).get_template(context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'image_full_width_block')

    class Meta:
        icon = 'image'
        label = 'Image Full-width'
        template = 'streams/image_full_width_block.html'


class ImageScrollBlock(blocks.StructBlock, ThemeableBlock):
    """Image Scroll"""

    image = ImageChooserBlock(required=True)
    hide_image_caption = blocks.BooleanBlock(required=False)

    def get_template(self, context, *args, **kwargs):
        standard_template = super(ImageScrollBlock, self).get_template(context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'image_scroll_block')

    class Meta:
        icon = 'image'
        label = 'Image'
        template = 'streams/image_scroll_block.html'


class ImageFullBleedBlock(blocks.StructBlock, ThemeableBlock):
    """Full bleed image"""

    image = ImageChooserBlock(required=True)
    hide_image_caption = blocks.BooleanBlock(required=False)

    def get_template(self, context, *args, **kwargs):
        standard_template = super(ImageFullBleedBlock, self).get_template(context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'image_full_bleed_block')

    class Meta:
        icon = 'image'
        label = 'Full Bleed Image'
        template = 'streams/image_full_bleed_block.html'


class InlineVideoBlock(blocks.PageChooserBlock, ThemeableBlock):
    """Inline video"""

    def get_template(self, context, *args, **kwargs):
        standard_template = super(InlineVideoBlock, self).get_template(context, *args, **kwargs)
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
    def get_template(self, context, *args, **kwargs):
        standard_template = super(HighlightTitleBlock, self).get_template(context, *args, **kwargs)
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
            'large_text',
            'link',
            'ol',
            'subscript',
            'superscript',
            'ul',
            'anchor',
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

    def get_template(self, context, *args, **kwargs):
        standard_template = super(ParagraphBlock, self).get_template(context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'paragraph_block')

    class Meta:
        icon = 'edit'
        label = 'Paragraph'
        template = 'streams/paragraph_block.html'


class PosterBlock(blocks.PageChooserBlock, ThemeableBlock):
    def get_template(self, context, *args, **kwargs):
        standard_template = super(PosterBlock, self).get_template(context, *args, **kwargs)
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

    def get_template(self, context, *args, **kwargs):
        standard_template = super(ReadMoreBlock, self).get_template(context, *args, **kwargs)
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

    def get_template(self, context, *args, **kwargs):
        standard_template = super(RecommendedBlock, self).get_template(context, *args, **kwargs)
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

    def get_template(self, context, *args, **kwargs):
        standard_template = super(PDFDownloadBlock, self).get_template(context, *args, **kwargs)
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

    def get_template(self, context, *args, **kwargs):
        standard_template = super(PullQuoteLeftBlock, self).get_template(context, *args, **kwargs)
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

    def get_template(self, context, *args, **kwargs):
        standard_template = super(PullQuoteRightBlock, self).get_template(context, *args, **kwargs)
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

    def get_template(self, context, *args, **kwargs):
        standard_template = super(TextBackgroundBlock, self).get_template(context, *args, **kwargs)
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

    def get_template(self, context, *args, **kwargs):
        standard_template = super(TextBorderBlock, self).get_template(context, *args, **kwargs)
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
        help_text='The URL of the tweet. Example: https://twitter.com/CIGIonline/status/1188821562440454144',
        verbose_name='Tweet URL',
    )

    def get_template(self, context, *args, **kwargs):
        standard_template = super(TweetBlock, self).get_template(context, *args, **kwargs)
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
            else:
                context['image_url'] = f'{context["page"].get_site().root_url}{settings.STATIC_URL}{value.get("image").get_rendition("fill-600x238").file.name}'

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
                else:
                    context['image_url'] = value.get("image_override").get_rendition("fill-600x238").file.name
            elif content_type != 'other' and content_page.image_hero:
                if content_page.image_hero.file.url.endswith('.gif'):
                    context['image_url'] = content_page.image_hero.file.name
                else:
                    context['image_url'] = content_page.image_hero.get_rendition("fill-600x238").file.name
                context['image_alt'] = content_page.image_hero.caption

            if context.get('image_url'):
                context['image_url'] = f'{context["page"].get_site().root_url}{settings.STATIC_URL}{context["image_url"]}'

            if not value.get('url'):
                context['url'] = content_page.full_url

            if content_type == 'Event' and context.get('text'):
                event_time = timezone.localtime(content_page.publishing_date, pytz.timezone(settings.TIME_ZONE)).strftime("%b. %-d – %-I:%M %p").replace('AM', 'a.m.').replace('PM', 'p.m.').replace('May.', 'May')
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
                text_soup = BeautifulSoup(context['text'].source, 'html.parser')
            for link in text_soup.findAll('a'):
                link['style'] = 'text-decoration: none; color: #ee1558;'
            if is_str:
                context['text'] = str(text_soup)
            else:
                context['text'].source = str(text_soup)

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


class ArticleCard(blocks.StructBlock):
    class ArticleCardTypeChoices(models.TextChoices):
        TINY = ('tiny', 'Tiny')
        SMALL = ('small', 'Small')
        MEDIUM = ('medium', 'Medium')
        LARGE = ('large', 'Large')

    page = blocks.PageChooserBlock(required=True, page_type='articles.ArticlePage')
    size = blocks.ChoiceBlock(choices=ArticleCardTypeChoices.choices, required=True)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        page = value.get('page').specific
        image = None
        if page.image_feature:
            image = page.image_feature
        elif page.image_hero:
            image = page.image_hero

        if image:
            if image.file.url.endswith('.gif'):
                context['image_src'] = image.file.url
                context['image_alt'] = image.title
            else:
                context['image'] = image
        else:
            context['image_src'] = 'static/assets/CIGI-default-recommended-thumb-1440x990.png'
            context['image_alt'] = 'CIGI Logo'

        context['title'] = page.feature_title if page.feature_title else page.title
        context['authors'] = page.authors.all()
        context['date'] = page.publishing_date
        context['description'] = page.feature_subtitle if page.feature_subtitle else page.short_description
        context['url'] = page.feature_url if page.feature_url else page.url
        context['topics'] = page.topics_sorted

        return context

    def get_template(self, context=None):
        if context:
            return f'streams/{self.meta.label.lower().replace(" ", "_")}_block_{context.get("block").value.get("size")}.html'
        return super().get_template(context)

    class Meta:
        icon = 'doc-full'
        label = 'Article Card'
        template = 'streams/article_card_block.html'


class PublicationCard(blocks.StructBlock):
    class PublicationCardTypeChoices(models.TextChoices):
        TINY = ('tiny', 'Tiny')
        SMALL = ('small', 'Small')
        MEDIUM = ('medium', 'Medium')
        MEDIUM_VERTICAL = ('medium_vertical', 'Medium Vertical')
        LARGE = ('large', 'Large')

    page = blocks.PageChooserBlock(required=True, page_type='publications.PublicationPage')
    size = blocks.ChoiceBlock(choices=PublicationCardTypeChoices.choices, required=True)
    use_hero_image = blocks.BooleanBlock(required=False)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        page = value.get('page').specific
        image = None
        if value.get('use_hero_image'):
            image = page.image_hero
        elif page.image_feature:
            image = page.image_feature
        elif page.image_cover:
            image = page.image_cover

        if image:
            if image.file.url.endswith('.gif'):
                context['image_src'] = image.file.url
                context['image_alt'] = image.title
            else:
                context['image'] = image
        else:
            context['image_src'] = 'static/assets/CIGI-default-recommended-thumb-1440x990.png'
            context['image_alt'] = 'CIGI Logo'

        context['title'] = page.feature_title if page.feature_title else page.title
        context['authors'] = page.authors.all()
        context['date'] = page.publishing_date
        context['description'] = page.feature_subtitle if page.feature_subtitle else page.short_description
        context['url'] = page.feature_url if page.feature_url else page.url
        context['topics'] = page.topics_sorted
        context['pdf_download'] = page.pdf_download

        return context

    def get_template(self, context=None):
        if context:
            return f'streams/{self.meta.label.lower().replace(" ", "_")}_block_{context.get("block").value.get("size")}.html'
        return super().get_template(context)

    class Meta:
        icon = 'doc-full'
        label = 'Publication Card'
        template = 'streams/publication_card_block.html'


class ArticleSeriesCard(blocks.StructBlock):
    class ArticleSeriesCardTypeChoices(models.TextChoices):
        TINY = ('tiny', 'Tiny')
        SMALL = ('small', 'Small')
        MEDIUM = ('medium', 'Medium')
        MEDIUM_VERTICAL = ('medium_vertical', 'Medium Vertical')
        LARGE = ('large', 'Large')

    page = blocks.PageChooserBlock(required=True, page_type='articles.ArticleSeriesPage')
    size = blocks.ChoiceBlock(choices=ArticleSeriesCardTypeChoices.choices, required=True)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        page = value.get('page').specific

        if page.image_poster:
            if page.image_poster.file.url.endswith('.gif'):
                context['poster_image_src'] = page.image_poster.file.url
                context['poster_image_alt'] = page.image_poster.title
            else:
                context['poster_image'] = page.image_poster
        else:
            context['poster_image_src'] = 'static/assets/CIGI-default-recommended-thumb-1440x990.png'
            context['poster_image_alt'] = 'CIGI Logo'

        if page.image_feature:
            if page.image_feature.file.url.endswith('.gif'):
                context['landscape_image_src'] = page.image_feature.file.url
                context['landscape_image_alt'] = page.image_feature.title
            else:
                context['landscape_image'] = page.image_feature
        elif page.image_hero:
            if page.image_hero.file.url.endswith('.gif'):
                context['landscape_image_src'] = page.image_hero.file.url
                context['landscape_image_alt'] = page.image_hero.title
            else:
                context['landscape_image'] = page.image_hero
        else:
            context['landscape_image_src'] = 'static/assets/CIGI-default-recommended-thumb-1440x990.png'
            context['landscape_image_alt'] = 'CIGI Logo'

        context['title'] = page.feature_title if page.feature_title else page.title
        context['authors'] = page.series_authors
        context['date'] = page.publishing_date
        context['description'] = page.feature_subtitle if page.feature_subtitle else page.short_description
        context['url'] = page.feature_url if page.feature_url else page.url
        context['topics'] = page.topics_sorted
        context['theme'] = page.theme

        return context

    def get_template(self, context=None):
        if context:
            return f'streams/{self.meta.label.lower().replace(" ", "_")}_block_{context.get("block").value.get("size")}.html'
        return super().get_template(context)

    class Meta:
        icon = 'doc-full'
        label = 'Article Series Card'
        template = 'streams/article_series_card_block.html'


class EventCard(blocks.StructBlock):
    class EventCardTypeChoices(models.TextChoices):
        TINY = ('tiny', 'Tiny')
        SMALL = ('small', 'Small')
        MEDIUM = ('medium', 'Medium')
        MEDIUM_VERTICAL = ('medium_vertical', 'Medium Vertical')
        LARGE = ('large', 'Large')

    page = blocks.PageChooserBlock(required=True, page_type='events.EventPage')
    size = blocks.ChoiceBlock(choices=EventCardTypeChoices.choices, required=True)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        page = value.get('page').specific
        image = None
        if page.image_feature:
            image = page.image_feature
        elif page.image_hero:
            image = page.image_hero

        if image:
            if image.file.url.endswith('.gif'):
                context['image_src'] = image.file.url
                context['image_alt'] = image.title
            else:
                context['image'] = image
        else:
            context['image_src'] = 'static/assets/CIGI-default-recommended-thumb-1440x990.png'
            context['image_alt'] = 'CIGI Logo'

        context['title'] = page.feature_title if page.feature_title else page.title
        context['authors'] = page.authors.all()
        context['date'] = page.publishing_date
        context['end_date'] = page.event_end
        context['event_type'] = page.get_event_type_display()
        context['event_access'] = page.get_event_access_display()
        context['event_format'] = page.event_format_string
        context['is_past'] = page.is_past()
        context['time_zone_label'] = page.time_zone_label
        context['url'] = page.feature_url if page.feature_url else page.url
        context['topics'] = page.topics_sorted
        context['registration_url'] = page.registration_url
        context['id'] = page.id

        return context

    def get_template(self, context=None):
        if context:
            return f'streams/{self.meta.label.lower().replace(" ", "_")}_block_{context.get("block").value.get("size")}.html'
        return super().get_template(context)

    class Meta:
        icon = 'date'
        label = 'Event Card'
        template = 'streams/event_card_block.html'


class EventsLandingEventCard(blocks.StructBlock):
    page = blocks.PageChooserBlock(required=True, page_type='events.EventPage')

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        page = value.get('page').specific
        image = None
        if page.image_feature:
            image = page.image_feature
        elif page.image_hero:
            image = page.image_hero

        if image:
            if image.file.url.endswith('.gif'):
                context['image_src'] = image.file.url
                context['image_alt'] = image.title
            else:
                context['image'] = image
        else:
            context['image_src'] = 'static/assets/CIGI-default-recommended-thumb-1440x990.png'
            context['image_alt'] = 'CIGI Logo'

        context['title'] = page.feature_title if page.feature_title else page.title
        context['authors'] = page.authors.all()
        context['date'] = page.publishing_date
        context['end_date'] = page.event_end
        context['event_type'] = page.get_event_type_display()
        context['event_access'] = page.get_event_access_display()
        context['event_format'] = page.event_format_string
        context['is_past'] = page.is_past()
        context['time_zone_label'] = page.time_zone_label
        context['url'] = page.feature_url if page.feature_url else page.url
        context['topics'] = page.topics_sorted
        context['registration_url'] = page.registration_url
        context['id'] = page.id
        if page.multimedia_page:
            if page.multimedia_page.specific.vimeo_url:
                context['vimeo_url'] = page.multimedia_page.specific.vimeo_url

        return context

    def get_template(self, context=None):
        if context:
            return 'streams/events_landing_event_card_block.html'
        return super().get_template(context)

    class Meta:
        icon = 'date'
        label = 'Event Card'
        template = 'streams/events_landing_event_card_block.html'


class MultimediaCard(blocks.StructBlock):
    class MultimediaCardTypeChoices(models.TextChoices):
        TINY = ('tiny', 'Tiny')
        SMALL = ('small', 'Small')
        MEDIUM = ('medium', 'Medium')
        LARGE = ('large', 'Large')

    class MultimediaCardMediaTypeChoices(models.TextChoices):
        VIDEO = ('video', 'Video')
        PODCAST = ('podcast', 'Podcast')

    page = blocks.PageChooserBlock(required=True, page_type='multimedia.MultimediaPage')
    size = blocks.ChoiceBlock(choices=MultimediaCardTypeChoices.choices, required=True)
    multimedia_type = blocks.ChoiceBlock(choices=MultimediaCardMediaTypeChoices.choices, required=True, default=MultimediaCardMediaTypeChoices.VIDEO)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        page = value.get('page').specific
        image = None
        if page.image_feature:
            image = page.image_feature
        elif page.image_hero:
            image = page.image_hero

        if image:
            if image.file.url.endswith('.gif'):
                context['image_src'] = image.file.url
                context['image_alt'] = image.title
            else:
                context['image'] = image
        else:
            context['image_src'] = 'static/assets/CIGI-default-recommended-thumb-1440x990.png'
            context['image_alt'] = 'CIGI Logo'

        if page.multimedia_type == 'video':
            youtube_id = page.multimedia_url.split('https://youtu.be/')[1]
            context['youtube_url'] = f'https://www.youtube.com/watch?v={youtube_id}'

        context['title'] = page.feature_title if page.feature_title else page.title
        context['authors'] = page.authors.all()
        context['date'] = page.publishing_date
        context['description'] = page.feature_subtitle if page.feature_subtitle else page.short_description
        context['url'] = page.feature_url if page.feature_url else page.url
        context['topics'] = page.topics_sorted
        context['length'] = page.length
        context['multimedia_type'] = page.multimedia_type
        context['multimedia_url'] = page.multimedia_url
        context['vimeo_url'] = page.vimeo_url

        return context

    def get_template(self, context=None):
        if context:
            return f'streams/{self.meta.label.lower().replace(" ", "_")}_block_{context.get("block").value.get("size")}.html'
        return super().get_template(context)

    class Meta:
        icon = 'media'
        label = 'Multimedia Card'
        template = 'streams/multimedia_card_block.html'


class ExpertCard(blocks.StructBlock):
    class ExpertCardTypeChoices(models.TextChoices):
        TINY = ('tiny', 'Tiny')
        SMALL = ('small', 'Small')
        MEDIUM = ('medium', 'Medium')

    page = blocks.PageChooserBlock(required=True, page_type='people.PersonPage')
    size = blocks.ChoiceBlock(choices=ExpertCardTypeChoices.choices, required=True)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        page = value.get('page').specific
        image = None
        if page.image_square:
            image = page.image_square

        if image:
            if image.file.url.endswith('.gif'):
                context['image_src'] = image.file.url
                context['image_alt'] = image.title
            else:
                context['image'] = image
        else:
            context['image_src'] = 'static/assets/CIGI-default-recommended-thumb-1440x990.png'
            context['image_alt'] = 'CIGI Logo'

        context['title'] = page.title
        context['description'] = page.short_bio
        context['url'] = page.url
        if page.latest_activity:
            context['latest_activity'] = [{
                'title': activity.title,
                'url': activity.url,
                'topics': activity.topics_sorted,
                'type': activity.contenttype
            } for activity in page.latest_activity]
        context['twitter'] = page.twitter_username
        context['linkedin_username'] = page.linkedin_username
        context['board_position'] = page.board_position
        context['expertise_list'] = page.expertise_list
        context['twitter_username'] = page.twitter_username

        return context

    def get_template(self, context=None):
        if context:
            return f'streams/{self.meta.label.lower().replace(" ", "_")}_block_{context.get("block").value.get("size")}.html'
        return super().get_template(context)

    class Meta:
        icon = 'user'
        label = 'Expert Card'
        template = 'streams/expert_card_block.html'


class TwitterCard(blocks.StructBlock):
    tweet = SnippetChooserBlock(required=True, target_model='social.Tweet')

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        urls = re.compile(r"((https?):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)", re.MULTILINE | re.UNICODE)
        tweet_text = urls.sub(r'<a href="\1" target="_blank">\1</a>', value.get('tweet').tweet_text)

        if value.get('tweet').tweet_media_link:
            tweet_media_link = value.get('tweet').tweet_media_link
        else:
            try:
                tweet_media_link = BeautifulSoup(tweet_text, parse_only=SoupStrainer('a')).find('a', href=True).get('href')
            except Exception:
                tweet_media_link = value.get('tweet').tweet_url
                error(traceback.format_exc())
        context['tweet_text'] = tweet_text
        context['tweet_media_link'] = tweet_media_link
        return context

    class Meta:
        icon = 'site'
        label = 'Twitter Card'
        template = 'streams/twitter_card_block.html'


class LinkedInCard(blocks.StructBlock):
    post = SnippetChooserBlock(required=True, target_model='social.LinkedinPost')

    class Meta:
        icon = 'site'
        label = 'LinkedIn Card'
        template = 'streams/linkedin_card_block.html'


class FacebookCard(blocks.StructBlock):
    post = SnippetChooserBlock(required=True, target_model='social.FacebookPost')

    class Meta:
        icon = 'site'
        label = 'Facebook Card'
        template = 'streams/facebook_card_block.html'


class AdCard(blocks.StructBlock):
    class AdCardTypeChoices(models.TextChoices):
        SMALL = ('small', 'Small')
        MEDIUM = ('medium', 'Medium')
        LARGE = ('large', 'Large')

    url = blocks.URLBlock(required=True)
    size = blocks.ChoiceBlock(choices=AdCardTypeChoices.choices, required=True)
    image = ImageChooserBlock(required=True)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        image = value.get('image')
        if image.file.url.endswith('.gif'):
            context['image_src'] = image.file.url
            context['image_alt'] = image.title
        else:
            context['image'] = image
        context['url'] = value.get('url')

        return context

    class Meta:
        icon = 'site'
        label = 'Ad Card'
        template = 'streams/ad_card_block.html'


class HomePageRowMostPopular(blocks.StructBlock):
    most_popular_cards = blocks.StreamBlock([
        ('article_card', ArticleCard()),
        ('publication_card', PublicationCard()),
        ('article_series_card', ArticleSeriesCard()),
        ('event_card', EventCard()),
        ('multimedia_card', MultimediaCard()),
        ('expert_card', ExpertCard()),
    ])

    class Meta:
        icon = 'list-ul'
        label = 'Most Popular Block'
        template = 'streams/home_page_row_most_popular_block.html'
        form_classname = 'most-popular-block'


class HomePageColumnBlock(blocks.StructBlock):
    column_cards = blocks.StreamBlock([
        ('article_card', ArticleCard()),
        ('publication_card', PublicationCard()),
        ('article_series_card', ArticleSeriesCard()),
        ('event_card', EventCard()),
        ('multimedia_card', MultimediaCard()),
        ('expert_card', ExpertCard()),
    ])

    class Meta:
        icon = 'list-ul'
        label = 'Column Block'
        template = 'streams/home_page_column_block.html'
        form_classname = 'column-block'


class SocialSwiperRow(blocks.StructBlock):
    social_swiper_cards = blocks.StreamBlock([
        ('twitter_card', TwitterCard()),
        ('linkedin_card', LinkedInCard()),
        ('facebook_card', FacebookCard()),
    ])

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context['bearer_token'] = os.environ['TWITTER_BEARER_TOKEN']
        return context

    class Meta:
        icon = 'list-ul'
        label = 'Social Swiper'
        template = 'streams/social_swiper_block.html'
        form_classname = 'social-swiper-block'


class HomePageRow(blocks.StructBlock):
    row = blocks.StreamBlock([
        ('article_card', ArticleCard()),
        ('publication_card', PublicationCard()),
        ('article_series_card', ArticleSeriesCard()),
        ('event_card', EventCard()),
        ('multimedia_card', MultimediaCard()),
        ('expert_card', ExpertCard()),
        ('ad_card', AdCard()),
        ('most_popular', HomePageRowMostPopular()),
        ('column_block', HomePageColumnBlock())
    ])
    grouped = blocks.BooleanBlock(required=False, default=False, help_text='Group cards into rows with a grey background.')

    class Meta:
        icon = 'list-ul'
        label = 'Row'
        template = 'streams/home_page_row_block.html'
        form_classname = 'row-block'


class ArticleLandingPageColumn(blocks.StructBlock):
    column = blocks.StreamBlock([
        ('article_card', ArticleCard()),
    ])

    class Meta:
        icon = 'list-ul'
        label = 'Column'
        template = 'streams/article_landing_page_column_block.html'
        form_classname = 'column-block'


class ArticleLandingPageRow(blocks.StructBlock):
    row = blocks.StreamBlock([
        ('article_card', ArticleCard()),
        ('column_block', ArticleLandingPageColumn()),
    ])

    class Meta:
        icon = 'list-ul'
        label = 'Row'
        template = 'streams/article_landing_page_row_block.html'
        form_classname = 'row-block'
