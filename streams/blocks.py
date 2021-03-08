from django.db import models
from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join
from wagtail.core import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.blocks import AbstractMediaChooserBlock


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


class ImageBlock(blocks.StructBlock, ThemeableBlock):
    """Image"""

    image = ImageChooserBlock(required=True)
    hide_image_caption = blocks.BooleanBlock(required=False)

    implemented_themes = [
        'cyber_series_opinion',
        'data_series_opinion',
        'longform_2_opinion',
    ]

    def get_template(self, context, *args, **kwargs):
        standard_template = super(ImageBlock, self).get_template(context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'image_block')

    class Meta:
        icon = 'image'
        label = 'Image'
        template = 'streams/image_block.html'


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
    ]

    def get_template(self, context, *args, **kwargs):
        standard_template = super(PullQuoteRightBlock, self).get_template(context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'pull_quote_right_block')

    class Meta:
        icon = 'edit'
        label = 'Pull Quote Right'
        template = 'streams/pull_quote_right_block.html'


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
            'pdf': 'https://gallery.mailchimp.com/3cafbe8a8401ae9ed275d2f75/images/caa024dc-e155-4c1f-a28b-2228770a99e2.png',
            'share_facebook': 'https://gallery.mailchimp.com/3cafbe8a8401ae9ed275d2f75/images/25daee19-d6c6-45ac-afd7-e168e3d410d3.png',
            'share_twitter': 'https://gallery.mailchimp.com/3cafbe8a8401ae9ed275d2f75/images/9f2bf138-03ac-45b7-b4db-7d27e663f15b.png',
            'share_linkedin': 'https://gallery.mailchimp.com/3cafbe8a8401ae9ed275d2f75/images/c7585d80-fbcd-43f6-996f-de088d02ca20.png',
            'rsvp': 'https://gallery.mailchimp.com/3cafbe8a8401ae9ed275d2f75/images/44282420-4212-477f-b678-5783c82dc51c.png',
            'listen': 'https://gallery.mailchimp.com/3cafbe8a8401ae9ed275d2f75/images/cff5d5c0-f14f-4c58-86b6-1d20c77dc09e.png',
            'explore': 'https://gallery.mailchimp.com/3cafbe8a8401ae9ed275d2f75/images/4b5ad389-bfb3-4819-8732-3eaf95e4965e.png',
            'subscribe': '',
            'learn_more': 'https://gallery.mailchimp.com/3cafbe8a8401ae9ed275d2f75/images/4b5ad389-bfb3-4819-8732-3eaf95e4965e.png',
            'follow': 'https://gallery.mailchimp.com/3cafbe8a8401ae9ed275d2f75/images/4ef4b224-1de1-4d41-8e8f-ca42068378d4.png',
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
            'share_facebook': 'Share (Facebook)',
            'share_linkedin': 'Share (LinkedIn)',
            'share_twitter': 'Share (Twitter)',
            'subscribe': 'Subscribe',
            'watch': 'Watch',
        }
        return cta_texts[cta]

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        if value['cta'] != 'no_cta':
            context['cta_image_link'] = self.cta_image_link(value['cta'])
            context['cta_text'] = self.cta_text(value['cta'])

        if 'content' in value:
            if 'title_override' in value and value['title_override']:
                context['title'] = value['title_override']
            else:
                context['title'] = value['content'].title

            if 'text_override' in value and value['text_override']:
                context['text'] = value['text_override']
            else:
                context['text'] = value['content'].specific.short_description

            if 'url' in value and value['url']:
                context['url'] = value['url']
            else:
                context['url'] = f'https://cigionline.org{value["content"].url}'
            
            if 'image_override' in value and value['image_override']:
                context['image_url'] = f'https://cigionline.org{value["image_override"].get_rendition("fill-600x238").url}'
            else:
                context['image_url'] = f'https://cigionline.org{value["content"].specific.image_hero.get_rendition("fill-600x238").url}'

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
        label = 'Content'
        template = 'streams/newsletter/featured_content_block.html'


class SocialBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    text = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
    )


class TextBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    text = blocks.RichTextBlock(
        features=['bold', 'italic', 'link'],
        required=False,
    )
