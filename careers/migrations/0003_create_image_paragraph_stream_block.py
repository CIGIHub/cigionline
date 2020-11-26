# Generated by Django 3.1.1 on 2020-10-09 14:56

from django.db import migrations
import streams.blocks
import wagtail.contrib.table_block.blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('careers', '0002_jobpostingpage_search_terms'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobpostinglistpage',
            name='body',
            field=wagtail.core.fields.StreamField([('paragraph', streams.blocks.ParagraphBlock()), ('image', streams.blocks.ParagraphImageBlock()), ('block_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.core.blocks.URLBlock(required=False)), ('link_text', wagtail.core.blocks.CharBlock(required=False))], template='streams/paragraph_type_blockquote.html')), ('table', wagtail.contrib.table_block.blocks.TableBlock()), ('text_border_block', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.RichTextBlock(required=True)), ('border_colour', wagtail.core.blocks.CharBlock(required=True))]))], blank=True),
        ),
        migrations.AlterField(
            model_name='jobpostingpage',
            name='description',
            field=wagtail.core.fields.StreamField([('paragraph', streams.blocks.ParagraphBlock()), ('image', streams.blocks.ParagraphImageBlock()), ('block_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.core.blocks.URLBlock(required=False)), ('link_text', wagtail.core.blocks.CharBlock(required=False))], template='streams/paragraph_type_blockquote.html')), ('table', wagtail.contrib.table_block.blocks.TableBlock()), ('text_border_block', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.RichTextBlock(required=True)), ('border_colour', wagtail.core.blocks.CharBlock(required=True))]))], blank=True),
        ),
    ]
