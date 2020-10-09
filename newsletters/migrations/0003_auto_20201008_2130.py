# Generated by Django 3.1.1 on 2020-10-09 01:30

from django.db import migrations
import streams.blocks
import wagtail.contrib.table_block.blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('newsletters', '0002_auto_20201008_2115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsletterlistpage',
            name='body',
            field=wagtail.core.fields.StreamField([('paragraph', streams.blocks.ParagraphBlock()), ('image', wagtail.images.blocks.ImageChooserBlock(template='streams/paragraph_type_image.html')), ('block_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.core.blocks.URLBlock(required=False)), ('link_text', wagtail.core.blocks.CharBlock(required=False))], template='streams/paragraph_type_blockquote.html')), ('table', wagtail.contrib.table_block.blocks.TableBlock()), ('text_border_block', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.RichTextBlock(required=True)), ('border_colour', wagtail.core.blocks.CharBlock(required=True))]))], blank=True),
        ),
    ]
