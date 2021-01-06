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

    def get_theme_template(self, standard_template, context, template_name):
        if context['page'] and hasattr(context['page'], 'theme') and \
                context['page'].theme and self.get_theme_dir(context['page'].theme.name) in self.implemented_themes:
            return f'themes/{self.get_theme_dir(context["page"].theme.name)}/streams/{template_name}.html'
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


class AuthorBlock(blocks.PageChooserBlock, ThemeableBlock):

    def get_template(self, context, *args, **kwargs):
        standard_template = super(AuthorBlock, self).get_template(context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'author_block')

    def get_api_representation(self, value, context=None):
        if value:
            return {
                'id': value.id,
                'title': value.title,
                'url': value.url,
            }

    class Meta:
        icon = 'user'
        label = 'Author'


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

    def get_template(self, context, *args, **kwargs):
        standard_template = super(BlockQuoteBlock, self).get_template(context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'block_quote_block')

    class Meta:
        icon = 'openquote'
        label = 'Blockquote Paragraph'
        template = 'streams/block_quote_block.html'


class ChartBlock(blocks.StructBlock, ThemeableBlock):
    """Chart image with title"""

    title = blocks.CharBlock(required=False)
    image = ImageChooserBlock(required=True)
    hide_image_caption = blocks.BooleanBlock(required=False)

    def get_template(self, context, *args, **kwargs):
        standard_template = super(ChartBlock, self).get_template(context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'chart_block')

    class Meta:
        icon = 'image'
        label = 'Chart'
        template = 'streams/chart_block.html'


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


class ImageBlock(blocks.StructBlock, ThemeableBlock):
    """Image"""

    image = ImageChooserBlock(required=True)
    hide_image_caption = blocks.BooleanBlock(required=False)

    def get_template(self, context, *args, **kwargs):
        standard_template = super(ImageBlock, self).get_template(context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'image_block')

    class Meta:
        icon = 'image'
        label = 'Image'
        template = 'streams/image_block.html'


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


class ParagraphBlock(blocks.RichTextBlock, ThemeableBlock):
    """Standard text paragraph."""
    def __init__(
        self, required=True, help_text=None, editor="default", features=None, **kwargs
    ):
        super().__init__(**kwargs)
        self.features = [
            'bold',
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
        ]

    def get_template(self, context, *args, **kwargs):
        standard_template = super(ParagraphBlock, self).get_template(context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'paragraph_block')

    class Meta:
        icon = 'edit'
        label = 'Paragraph'
        template = 'streams/paragraph_block.html'


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

    def get_template(self, context, *args, **kwargs):
        standard_template = super(PullQuoteRightBlock, self).get_template(context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'pull_quote_right_block')

    class Meta:
        icon = 'edit'
        label = 'Pull Quote Right'
        template = 'streams/pull_quote_right_block.html'


class SpeakersBlock(blocks.PageChooserBlock, ThemeableBlock):

    def get_template(self, context, *args, **kwargs):
        standard_template = super(SpeakersBlock, self).get_template(context, *args, **kwargs)
        return self.get_theme_template(standard_template, context, 'speakers_block')

    def get_api_representation(self, value, context=None):
        if value:
            return {
                'id': value.id,
                'title': value.title,
                'url': value.url,
            }

    class Meta:
        icon = 'user'
        label = 'Speakers'


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
