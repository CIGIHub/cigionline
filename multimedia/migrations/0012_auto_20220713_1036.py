# Generated by Django 3.2.13 on 2022-07-13 14:36

from django.db import migrations
import streams.blocks
import wagtail.blocks
import wagtail.documents.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0011_increase_feature_subtitle_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multimedialistpage',
            name='body',
            field=wagtail.fields.StreamField([('block_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('author_title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.blocks.URLBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(required=False))])), ('embedded_multimedia', wagtail.blocks.StructBlock([('multimedia_url', wagtail.blocks.URLBlock(required=True)), ('title', wagtail.blocks.CharBlock(required=False))])), ('embedded_video', wagtail.blocks.StructBlock([('video_url', wagtail.blocks.URLBlock(required=True)), ('caption', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('aspect_ratio', wagtail.blocks.ChoiceBlock(choices=[('none', 'None'), ('landscape', 'Landscape'), ('square', 'Square')]))])), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False))])), ('inline_video', streams.blocks.InlineVideoBlock(page_type=['multimedia.MultimediaPage'])), ('paragraph', streams.blocks.ParagraphBlock()), ('table', streams.blocks.TableStreamBlock()), ('text_background_block', streams.blocks.TextBackgroundBlock(features=['bold', 'italic', 'link']))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='multimedialistpage',
            name='hero_link',
            field=wagtail.fields.StreamField([('hero_link', wagtail.blocks.StructBlock([('hero_link_text', wagtail.blocks.CharBlock(required=True)), ('hero_link_url', wagtail.blocks.CharBlock(required=True)), ('hero_link_icon', wagtail.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))])), ('hero_document', wagtail.blocks.StructBlock([('hero_link_text', wagtail.blocks.CharBlock(required=True)), ('hero_link_document', wagtail.documents.blocks.DocumentChooserBlock(required=True)), ('hero_link_icon', wagtail.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))]))], blank=True, help_text='Text with link to url, email or document and optional icon that appears below the page title in the hero section.', use_json_field=True),
        ),
        migrations.AlterField(
            model_name='multimediapage',
            name='body',
            field=wagtail.fields.StreamField([('block_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('author_title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.blocks.URLBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(required=False))])), ('embedded_multimedia', wagtail.blocks.StructBlock([('multimedia_url', wagtail.blocks.URLBlock(required=True)), ('title', wagtail.blocks.CharBlock(required=False))])), ('embedded_video', wagtail.blocks.StructBlock([('video_url', wagtail.blocks.URLBlock(required=True)), ('caption', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('aspect_ratio', wagtail.blocks.ChoiceBlock(choices=[('none', 'None'), ('landscape', 'Landscape'), ('square', 'Square')]))])), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False))])), ('inline_video', streams.blocks.InlineVideoBlock(page_type=['multimedia.MultimediaPage'])), ('paragraph', streams.blocks.ParagraphBlock()), ('table', streams.blocks.TableStreamBlock()), ('text_background_block', streams.blocks.TextBackgroundBlock(features=['bold', 'italic', 'link']))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='multimediapage',
            name='hero_link',
            field=wagtail.fields.StreamField([('hero_link', wagtail.blocks.StructBlock([('hero_link_text', wagtail.blocks.CharBlock(required=True)), ('hero_link_url', wagtail.blocks.CharBlock(required=True)), ('hero_link_icon', wagtail.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))])), ('hero_document', wagtail.blocks.StructBlock([('hero_link_text', wagtail.blocks.CharBlock(required=True)), ('hero_link_document', wagtail.documents.blocks.DocumentChooserBlock(required=True)), ('hero_link_icon', wagtail.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))]))], blank=True, help_text='Text with link to url, email or document and optional icon that appears below the page title in the hero section.', use_json_field=True),
        ),
        migrations.AlterField(
            model_name='multimediapage',
            name='podcast_guests',
            field=wagtail.fields.StreamField([('guest', wagtail.blocks.CharBlock(required=True))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='multimediapage',
            name='transcript',
            field=wagtail.fields.StreamField([('accordion', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=True)), ('text', wagtail.blocks.RichTextBlock(features=['bold', 'h3', 'h4', 'italic', 'link', 'ol', 'ul'], required=True))])), ('read_more', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=True)), ('text', wagtail.blocks.RichTextBlock(features=['bold', 'h3', 'h4', 'italic', 'link', 'ol', 'ul'], required=True))]))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='multimediapage',
            name='video_chapters',
            field=wagtail.fields.StreamField([('video_chapter', wagtail.blocks.StructBlock([('chapter_title', wagtail.blocks.CharBlock(required=True)), ('location_time', wagtail.blocks.IntegerBlock(required=True)), ('chapter_description', wagtail.blocks.TextBlock(required=False))]))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='multimediaseriespage',
            name='body',
            field=wagtail.fields.StreamField([('block_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('author_title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.blocks.URLBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(required=False))])), ('embedded_multimedia', wagtail.blocks.StructBlock([('multimedia_url', wagtail.blocks.URLBlock(required=True)), ('title', wagtail.blocks.CharBlock(required=False))])), ('embedded_video', wagtail.blocks.StructBlock([('video_url', wagtail.blocks.URLBlock(required=True)), ('caption', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('aspect_ratio', wagtail.blocks.ChoiceBlock(choices=[('none', 'None'), ('landscape', 'Landscape'), ('square', 'Square')]))])), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False))])), ('inline_video', streams.blocks.InlineVideoBlock(page_type=['multimedia.MultimediaPage'])), ('paragraph', streams.blocks.ParagraphBlock()), ('table', streams.blocks.TableStreamBlock()), ('text_background_block', streams.blocks.TextBackgroundBlock(features=['bold', 'italic', 'link']))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='multimediaseriespage',
            name='hero_link',
            field=wagtail.fields.StreamField([('hero_link', wagtail.blocks.StructBlock([('hero_link_text', wagtail.blocks.CharBlock(required=True)), ('hero_link_url', wagtail.blocks.CharBlock(required=True)), ('hero_link_icon', wagtail.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))])), ('hero_document', wagtail.blocks.StructBlock([('hero_link_text', wagtail.blocks.CharBlock(required=True)), ('hero_link_document', wagtail.documents.blocks.DocumentChooserBlock(required=True)), ('hero_link_icon', wagtail.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))]))], blank=True, help_text='Text with link to url, email or document and optional icon that appears below the page title in the hero section.', use_json_field=True),
        ),
        migrations.AlterField(
            model_name='multimediaseriespage',
            name='podcast_subscribe_buttons',
            field=wagtail.fields.StreamField([('podcast_subscribe_button', wagtail.blocks.StructBlock([('label', wagtail.blocks.CharBlock(required=True)), ('url', wagtail.blocks.URLBlock(required=True))]))], blank=True, help_text='A list of subscribe links to various podcast providers', use_json_field=True, verbose_name='Podcast Subscribe Buttons'),
        ),
    ]