# Generated by Django 3.2.18 on 2024-04-24 14:50

from django.db import migrations
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0023_auto_20240209_1333'),
    ]

    operations = [
        migrations.AddField(
            model_name='multimediaseriespage',
            name='featured_episodes',
            field=wagtail.fields.StreamField([('featured_episode', wagtail.blocks.StructBlock([('episode', wagtail.blocks.PageChooserBlock(page_type=['multimedia.MultimediaPage'], required=True))]))], blank=True, use_json_field=True),
        ),
    ]