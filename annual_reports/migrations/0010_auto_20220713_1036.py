# Generated by Django 3.2.13 on 2022-07-13 14:36

from django.db import migrations
import streams.blocks
import wagtail.blocks
import wagtail.documents.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('annual_reports', '0009_increase_feature_subtitle_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annualreportlistpage',
            name='body',
            field=wagtail.fields.StreamField([('block_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('author_title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.blocks.URLBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(required=False))])), ('embedded_multimedia', wagtail.blocks.StructBlock([('multimedia_url', wagtail.blocks.URLBlock(required=True)), ('title', wagtail.blocks.CharBlock(required=False))])), ('embedded_video', wagtail.blocks.StructBlock([('video_url', wagtail.blocks.URLBlock(required=True)), ('caption', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('aspect_ratio', wagtail.blocks.ChoiceBlock(choices=[('none', 'None'), ('landscape', 'Landscape'), ('square', 'Square')]))])), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False))])), ('inline_video', streams.blocks.InlineVideoBlock(page_type=['multimedia.MultimediaPage'])), ('paragraph', streams.blocks.ParagraphBlock()), ('table', streams.blocks.TableStreamBlock()), ('text_background_block', streams.blocks.TextBackgroundBlock(features=['bold', 'italic', 'link']))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='annualreportlistpage',
            name='featured_reports',
            field=wagtail.fields.StreamField([('featured_report', wagtail.blocks.PageChooserBlock(page_type=['annual_reports.AnnualReportPage'], required=True))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='annualreportlistpage',
            name='hero_link',
            field=wagtail.fields.StreamField([('hero_link', wagtail.blocks.StructBlock([('hero_link_text', wagtail.blocks.CharBlock(required=True)), ('hero_link_url', wagtail.blocks.CharBlock(required=True)), ('hero_link_icon', wagtail.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))])), ('hero_document', wagtail.blocks.StructBlock([('hero_link_text', wagtail.blocks.CharBlock(required=True)), ('hero_link_document', wagtail.documents.blocks.DocumentChooserBlock(required=True)), ('hero_link_icon', wagtail.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))]))], blank=True, help_text='Text with link to url, email or document and optional icon that appears below the page title in the hero section.', use_json_field=True),
        ),
        migrations.AlterField(
            model_name='annualreportlistpage',
            name='search_terms',
            field=wagtail.fields.StreamField([('search_term', wagtail.blocks.CharBlock())], blank=True, help_text='A list of search terms for which this page will be elevated in the search results.', use_json_field=True),
        ),
        migrations.AlterField(
            model_name='annualreportpage',
            name='search_terms',
            field=wagtail.fields.StreamField([('search_term', wagtail.blocks.CharBlock())], blank=True, help_text='A list of search terms for which this page will be elevated in the search results.', use_json_field=True),
        ),
    ]
