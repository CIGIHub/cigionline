from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join
from wagtail.core import blocks
from wagtail.documents.blocks import DocumentChooserBlock
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


class AuthorBlock(blocks.PageChooserBlock):
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

    title = blocks.CharBlock(required=False)
    image = ImageChooserBlock(required=True)
    hide_image_caption = blocks.BooleanBlock(required=False)

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


class PDFDownloadBlock(blocks.StructBlock):
    file = DocumentChooserBlock(required=True)
    button_text = blocks.CharBlock(
        required=False,
        help_text='Optional text to replace the button text. If left empty, the button will read "Download PDF".'
    )

    def get_api_representation(self, value, context=None):
        if value:
            return {
                'button_text': value.get('button_text'),
                'url': value.get('file').file.url,
            }

    class Meta:
        icon = 'download-alt'
        label = 'PDF Download'


class SpeakersBlock(blocks.PageChooserBlock):
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


class TweetBlock(blocks.StructBlock):
    """Tweet Block"""

    tweet_id = blocks.IntegerBlock(
                required=True,
                help_text='Insert the ID of the tweet. It can be found in the browser URL at the end. Example: https://twitter.com/CIGIonline/status/1188821562440454144 -> The tweet id is 1188821562440454144',
                verbose_name='Tweet ID',
            )
    class Meta:
        icon = 'social'
        label = 'Tweet'
        template = 'streams/tweet_block.html'

