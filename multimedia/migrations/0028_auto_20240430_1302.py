# Generated by Django 3.2.18 on 2024-04-30 17:02

from django.db import migrations
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0027_auto_20240426_1136'),
    ]

    operations = [
        migrations.AddField(
            model_name='multimediapage',
            name='podcast_chapters',
            field=wagtail.fields.StreamField([('podcast_chapter', wagtail.blocks.StructBlock([('text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False)), ('timestamp', wagtail.blocks.StructBlock([('hours', wagtail.blocks.IntegerBlock(required=False)), ('minutes', wagtail.blocks.IntegerBlock(required=False)), ('seconds', wagtail.blocks.IntegerBlock(required=False))]))]))], blank=True, help_text='A list of chapters for the podcast', use_json_field=True, verbose_name='Podcast Chapters'),
        ),
        migrations.AlterField(
            model_name='multimediaseriespage',
            name='podcast_hosts',
            field=wagtail.fields.StreamField([('podcast_host', wagtail.blocks.StructBlock([('host', wagtail.blocks.PageChooserBlock(page_type=['people.PersonPage'], required=True)), ('bio', wagtail.blocks.RichTextBlock(required=False))]))], blank=True, help_text='Hosts of the podcast', use_json_field=True, verbose_name='Podcast Hosts'),
        ),
    ]