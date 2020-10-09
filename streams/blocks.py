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
