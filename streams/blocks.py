from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock


class ParagraphBlock(blocks.RichTextBlock):
    """Standard text paragraph."""

    class Meta:
        icon = 'edit'
        label = 'Paragraph'
        template = 'streams/paragraph_block.html'


class ParagraphImageBlock(ImageChooserBlock):
    """Image paragraph"""

    class Meta:
        icon = 'image'
        label = 'Image Paragraph'
        template = 'streams/paragraph_type_image.html'


class ParagraphBlockQuote(blocks.StructBlock):
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
        template = 'streams/paragraph_type_blockquote.html'
