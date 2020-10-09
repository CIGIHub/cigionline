# Generated by Django 3.1.1 on 2020-10-09 01:15

from django.db import migrations
import streams.blocks
import wagtail.contrib.table_block.blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0002_populate_project_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectpage',
            name='body',
            field=wagtail.core.fields.StreamField([('paragraph', streams.blocks.ParagraphBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('block_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.core.blocks.URLBlock(required=False)), ('link_text', wagtail.core.blocks.CharBlock(required=False))], template='streams/paragraph_type_blockquote.html')), ('table', wagtail.contrib.table_block.blocks.TableBlock()), ('text_border_block', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.RichTextBlock(required=True)), ('border_colour', wagtail.core.blocks.CharBlock(required=True))])), ('poster_block', wagtail.core.blocks.PageChooserBlock(page_type=['publications.PublicationPage'], required=True)), ('igc_timeline', wagtail.core.blocks.StructBlock([('date', wagtail.core.blocks.CharBlock(required=True)), ('title', wagtail.core.blocks.CharBlock(required=False)), ('body', wagtail.core.blocks.RichTextBlock(required=False)), ('location', wagtail.core.blocks.CharBlock(required=False)), ('countries_represented', wagtail.images.blocks.ImageChooserBlock(required=False)), ('outcomes', wagtail.core.blocks.StreamBlock([('outcome', wagtail.core.blocks.StructBlock([('date', wagtail.core.blocks.DateBlock(required=False)), ('text', wagtail.core.blocks.RichTextBlock(required=False))]))], required=False)), ('witnesses', wagtail.core.blocks.StreamBlock([('witness_date', wagtail.core.blocks.StructBlock([('date', wagtail.core.blocks.DateBlock(required=False)), ('witnesses', wagtail.core.blocks.StreamBlock([('witnesses_full_session', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(required=False)), ('witness_transcript', wagtail.core.blocks.URLBlock(required=False)), ('witness_video', wagtail.core.blocks.URLBlock(required=False))])), ('witness', wagtail.core.blocks.StructBlock([('name', wagtail.core.blocks.CharBlock(required=False)), ('title', wagtail.core.blocks.CharBlock(required=False)), ('witness_transcript', wagtail.core.blocks.URLBlock(required=False)), ('witness_video', wagtail.core.blocks.URLBlock(required=False))]))]))]))], required=False))]))], blank=True),
        ),
    ]
