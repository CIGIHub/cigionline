# Generated by Django 3.2.18 on 2024-03-25 19:14

from django.db import migrations, models
import django.db.models.deletion
import streams.blocks
import wagtail.blocks
import wagtail.documents.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('menus', '0003_increase_menu_item_title_length'),
        ('images', '0003_auto_20230925_1253'),
        ('articles', '0041_add_series_items_description_to_opinion_series'),
    ]

    operations = [
        migrations.AddField(
            model_name='articleserieslistpage',
            name='body',
            field=wagtail.fields.StreamField([('block_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('author_title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.blocks.URLBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(required=False))])), ('embedded_multimedia', wagtail.blocks.StructBlock([('multimedia_url', wagtail.blocks.URLBlock(required=True)), ('title', wagtail.blocks.CharBlock(required=False))])), ('embedded_video', wagtail.blocks.StructBlock([('video_url', wagtail.blocks.URLBlock(required=True)), ('caption', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('aspect_ratio', wagtail.blocks.ChoiceBlock(choices=[('none', 'None'), ('landscape', 'Landscape'), ('square', 'Square')]))])), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False))])), ('inline_video', streams.blocks.InlineVideoBlock(page_type=['multimedia.MultimediaPage'])), ('paragraph', streams.blocks.ParagraphBlock()), ('table', streams.blocks.TableStreamBlock()), ('text_background_block', streams.blocks.TextBackgroundBlock(features=['bold', 'italic', 'link'])), ('persons_list_block', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('bio_source_field', wagtail.blocks.ChoiceBlock(choices=[('full_bio', 'Full Biography'), ('short_bio', 'Short Biography')], help_text="Select the field from the person's page to populate their biography in this block. Default to 'Full Biography'.", max_choices=1, required=False, verbose_name='Biography Source Field')), ('persons', wagtail.blocks.StreamBlock([('person', wagtail.blocks.PageChooserBlock(page_type=['people.PersonPage'], required=True))], required=True))])), ('publications_list_block', wagtail.blocks.StructBlock([('publication_type', wagtail.blocks.PageChooserBlock(help_text='Select a publication type to automatically populate with this type of publications.', page_type=['publications.PublicationTypePage'], required=False)), ('publications', wagtail.blocks.StreamBlock([('publication', wagtail.blocks.PageChooserBlock(page_type=['publications.PublicationPage'], required=True))], required=False))])), ('additional_pages_block', wagtail.blocks.StructBlock([('pages', wagtail.blocks.StreamBlock([('page', wagtail.blocks.PageChooserBlock(required=True))], required=True))]))], blank=True, use_json_field=True),
        ),
        migrations.AddField(
            model_name='articleserieslistpage',
            name='hero_link',
            field=wagtail.fields.StreamField([('hero_link', wagtail.blocks.StructBlock([('hero_link_text', wagtail.blocks.CharBlock(required=True)), ('hero_link_url', wagtail.blocks.CharBlock(required=True)), ('hero_link_icon', wagtail.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))])), ('hero_document', wagtail.blocks.StructBlock([('hero_link_text', wagtail.blocks.CharBlock(required=True)), ('hero_link_document', wagtail.documents.blocks.DocumentChooserBlock(required=True)), ('hero_link_icon', wagtail.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))]))], blank=True, help_text='Text with link to url, email or document and optional icon that appears below the page title in the hero section.', use_json_field=True),
        ),
        migrations.AddField(
            model_name='articleserieslistpage',
            name='image_hero',
            field=models.ForeignKey(blank=True, help_text='A large image to be displayed prominently on the page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.cigionlineimage', verbose_name='Hero Image'),
        ),
        migrations.AddField(
            model_name='articleserieslistpage',
            name='submenu',
            field=models.ForeignKey(blank=True, help_text='Select a submenu to appear in the right section of the hero.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menus.menu', verbose_name='Submenu'),
        ),
        migrations.AddField(
            model_name='articleserieslistpage',
            name='subtitle',
            field=wagtail.fields.RichTextField(blank=True),
        ),
    ]
