# Generated by Django 3.1.7 on 2021-03-20 01:26

from django.db import migrations, models
import django.db.models.deletion
import streams.blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.documents.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0023_add_choose_permissions'),
        ('menus', '0002_populate_menus'),
        ('articles', '0005_update_table_stream_block'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlelandingpage',
            name='body',
            field=wagtail.core.fields.StreamField([('block_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.core.blocks.URLBlock(required=False)), ('link_text', wagtail.core.blocks.CharBlock(required=False))])), ('embedded_multimedia', wagtail.core.blocks.StructBlock([('multimedia_url', wagtail.core.blocks.URLBlock(required=True)), ('title', wagtail.core.blocks.CharBlock(required=False))])), ('embedded_video', wagtail.core.blocks.StructBlock([('video_url', wagtail.core.blocks.URLBlock(required=True)), ('caption', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('aspect_ratio', wagtail.core.blocks.ChoiceBlock(choices=[('none', 'None'), ('landscape', 'Landscape'), ('square', 'Square')]))])), ('image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.core.blocks.BooleanBlock(required=False))])), ('inline_video', streams.blocks.InlineVideoBlock(page_type=['multimedia.MultimediaPage'])), ('paragraph', streams.blocks.ParagraphBlock()), ('table', streams.blocks.TableStreamBlock()), ('text_background_block', streams.blocks.TextBackgroundBlock(features=['bold', 'italic', 'link']))], blank=True),
        ),
        migrations.AddField(
            model_name='articlelandingpage',
            name='hero_link',
            field=wagtail.core.fields.StreamField([('hero_link', wagtail.core.blocks.StructBlock([('hero_link_text', wagtail.core.blocks.CharBlock(required=True)), ('hero_link_url', wagtail.core.blocks.CharBlock(required=True)), ('hero_link_icon', wagtail.core.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))])), ('hero_document', wagtail.core.blocks.StructBlock([('hero_link_text', wagtail.core.blocks.CharBlock(required=True)), ('hero_link_document', wagtail.documents.blocks.DocumentChooserBlock(required=True)), ('hero_link_icon', wagtail.core.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))]))], blank=True, help_text='Text with link to url, email or document and optional icon that appears below the page title in the hero section.'),
        ),
        migrations.AddField(
            model_name='articlelandingpage',
            name='image_hero',
            field=models.ForeignKey(blank=True, help_text='A large image to be displayed prominently on the page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Hero Image'),
        ),
        migrations.AddField(
            model_name='articlelandingpage',
            name='submenu',
            field=models.ForeignKey(blank=True, help_text='Select a submenu to appear in the right section of the hero.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menus.menu', verbose_name='Submenu'),
        ),
        migrations.AddField(
            model_name='articlelandingpage',
            name='subtitle',
            field=wagtail.core.fields.RichTextField(blank=True),
        ),
    ]
