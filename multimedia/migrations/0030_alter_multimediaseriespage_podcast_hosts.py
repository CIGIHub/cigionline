# Generated by Django 3.2.18 on 2024-05-02 22:18

from django.db import migrations
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0029_alter_multimediapage_podcast_chapters'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multimediaseriespage',
            name='podcast_hosts',
            field=wagtail.fields.StreamField([('podcast_host', wagtail.blocks.StructBlock([('host', wagtail.blocks.PageChooserBlock(page_type=['people.PersonPage'], required=True)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('bio', wagtail.blocks.RichTextBlock(required=False))]))], blank=True, help_text='Hosts of the podcast', use_json_field=True, verbose_name='Podcast Hosts'),
        ),
    ]
