from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join
from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.blocks import AbstractMediaChooserBlock


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


class AutoPlayVideoBlock(blocks.StructBlock):
    video = VideoBlock(required=False)
    caption = blocks.CharBlock(required=False)

    class Meta:
        icon = 'media'
        label = 'Autoplay Video'
        template = 'streams/autoplay_video_block.html'


class BlockQuoteBlock(blocks.StructBlock):
    """Block quote paragraph with optional image and link"""

    quote = blocks.RichTextBlock(required=True)
    quote_author = blocks.CharBlock(required=False)
    author_title = blocks.CharBlock(required=False)
    image = ImageChooserBlock(required=False)
    link_url = blocks.URLBlock(required=False)
    link_text = blocks.CharBlock(required=False)

    class Meta:
        icon = 'openquote'
        label = 'Blockquote Paragraph'
        template = 'streams/block_quote_block.html'


class ChartBlock(blocks.StructBlock):
    """Chart image with title"""

    image = ImageChooserBlock(required=True)
    hide_image_caption = blocks.BooleanBlock(required=False)
    title = blocks.CharBlock(required=True)

    class Meta:
        icon = 'image'
        label = 'Chart'
        template = 'streams/chart_block.html'


class ImageBlock(blocks.StructBlock):
    """Image"""

    image = ImageChooserBlock(required=True)
    hide_image_caption = blocks.BooleanBlock(required=False)

    class Meta:
        icon = 'image'
        label = 'Image'
        template = 'streams/image_block.html'


class ParagraphBlock(blocks.RichTextBlock):
    """Standard text paragraph."""

    class Meta:
        icon = 'edit'
        label = 'Paragraph'
        template = 'streams/paragraph_block.html'
