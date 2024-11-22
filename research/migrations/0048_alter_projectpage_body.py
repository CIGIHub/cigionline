# Generated by Django 5.0.6 on 2024-11-22 15:54

import streams.blocks
import wagtail.blocks
import wagtail.documents.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0047_alter_projectpage_body'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectpage',
            name='body',
            field=wagtail.fields.StreamField([('block_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('author_title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.blocks.URLBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(required=False))])), ('embedded_multimedia', wagtail.blocks.StructBlock([('multimedia_url', wagtail.blocks.URLBlock(required=True)), ('title', wagtail.blocks.CharBlock(required=False))])), ('embedded_video', wagtail.blocks.StructBlock([('video_url', wagtail.blocks.URLBlock(required=True)), ('caption', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('aspect_ratio', wagtail.blocks.ChoiceBlock(choices=[('none', 'None'), ('landscape', 'Landscape'), ('square', 'Square')]))])), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False))])), ('inline_video', streams.blocks.InlineVideoBlock(page_type=['multimedia.MultimediaPage'])), ('paragraph', streams.blocks.ParagraphBlock()), ('slider_gallery', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('slides', wagtail.blocks.StreamBlock([('slide', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock(required=False))]))], required=False))])), ('table', streams.blocks.TableStreamBlock()), ('text_background_block', streams.blocks.TextBackgroundBlock(features=['bold', 'italic', 'link'])), ('persons_list_block', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('bio_source_field', wagtail.blocks.ChoiceBlock(choices=[('full_bio', 'Full Biography'), ('short_bio', 'Short Biography')], help_text="Select the field from the person's page to populate their biography in this block. Default to 'Full Biography'.", max_choices=1, required=False, verbose_name='Biography Source Field')), ('persons', wagtail.blocks.StreamBlock([('person', wagtail.blocks.PageChooserBlock(page_type=['people.PersonPage'], required=True))], required=True))])), ('publications_list_block', wagtail.blocks.StructBlock([('publication_type', wagtail.blocks.PageChooserBlock(help_text='Select a publication type to automatically populate with this type of publications.', page_type=['publications.PublicationTypePage'], required=False)), ('publications', wagtail.blocks.StreamBlock([('publication', wagtail.blocks.PageChooserBlock(page_type=['publications.PublicationPage'], required=True))], required=False))])), ('additional_pages_block', wagtail.blocks.StructBlock([('pages', wagtail.blocks.StreamBlock([('page', wagtail.blocks.PageChooserBlock(required=True))], required=True))])), ('poster_block', streams.blocks.PosterBlock(page_type=['publications.PublicationPage'], required=True)), ('recommended', streams.blocks.RecommendedBlock()), ('text_border_block', wagtail.blocks.StructBlock([('text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('border_colour', wagtail.blocks.CharBlock(required=False))])), ('additional_file', wagtail.blocks.StructBlock([('file', wagtail.documents.blocks.DocumentChooserBlock(required=True)), ('page', wagtail.blocks.PageChooserBlock(required=False)), ('title', wagtail.blocks.CharBlock(required=False)), ('description', wagtail.blocks.RichTextBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False))])), ('ges_events', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('project', wagtail.blocks.PageChooserBlock(page_type=['research.ProjectPage'], required=True))])), ('ges_highlights', wagtail.blocks.StructBlock([('slides', wagtail.blocks.StreamBlock([('slide', wagtail.blocks.StructBlock([('label', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('caption', wagtail.blocks.RichTextBlock(required=False))]))])), ('title', wagtail.blocks.CharBlock(required=False)), ('description', wagtail.blocks.RichTextBlock(required=False)), ('pdf', wagtail.documents.blocks.DocumentChooserBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False))])), ('ges_slide', wagtail.blocks.StructBlock([('label', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('caption', wagtail.blocks.RichTextBlock(required=False))])), ('ges_slide_deck', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('title', wagtail.blocks.CharBlock(required=False)), ('description', wagtail.blocks.RichTextBlock(required=False)), ('download', wagtail.documents.blocks.DocumentChooserBlock(required=False)), ('last_updated', wagtail.blocks.DateBlock(required=False))])), ('ges_data', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('description', wagtail.blocks.RichTextBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('download', wagtail.documents.blocks.DocumentChooserBlock(required=False))])), ('ges_raw_data', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('description', wagtail.blocks.RichTextBlock(required=False)), ('download', wagtail.documents.blocks.DocumentChooserBlock(required=False))])), ('chair', wagtail.blocks.StructBlock([('chair', wagtail.blocks.PageChooserBlock(help_text='Internal profile if available.', page_type=['people.PersonPage'], required=False)), ('url', wagtail.blocks.URLBlock(help_text='URL to their external profile if internal profile is not available.', required=False)), ('name', wagtail.blocks.CharBlock(help_text='Chair name if internal profile is not available.', required=False)), ('position', wagtail.blocks.RichTextBlock(help_text='Override internal profile position.', required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(help_text='Override internal profile image.', required=False))]))], blank=True),
        ),
    ]
