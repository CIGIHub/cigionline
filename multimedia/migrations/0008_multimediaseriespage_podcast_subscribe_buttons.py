# Generated by Django 3.2.4 on 2021-10-29 15:59

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0007_multimediapage_image_poster'),
    ]

    operations = [
        migrations.AddField(
            model_name='multimediaseriespage',
            name='podcast_subscribe_buttons',
            field=wagtail.core.fields.StreamField([('podcast_subscribe_button', wagtail.core.blocks.StructBlock([('label', wagtail.core.blocks.CharBlock(required=True)), ('url', wagtail.core.blocks.URLBlock(required=True))]))], blank=True, help_text='A list of search terms for which this page will be elevated in the search results.'),
        ),
    ]