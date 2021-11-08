# Generated by Django 3.2.4 on 2021-11-03 18:05

from django.db import migrations, models
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0008_multimediaseriespage_podcast_subscribe_buttons'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='multimediaseriespage',
            name='podcast_apple_url',
        ),
        migrations.RemoveField(
            model_name='multimediaseriespage',
            name='podcast_google_url',
        ),
        migrations.RemoveField(
            model_name='multimediaseriespage',
            name='podcast_spotify_url',
        ),
        migrations.AddField(
            model_name='multimediaseriespage',
            name='podcast_season_tagline',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='multimediaseriespage',
            name='podcast_subscribe_buttons',
            field=wagtail.core.fields.StreamField([('podcast_subscribe_button', wagtail.core.blocks.StructBlock([('label', wagtail.core.blocks.CharBlock(required=True)), ('url', wagtail.core.blocks.URLBlock(required=True))]))], blank=True, help_text='A list of subscribe links to various podcast providers', verbose_name='Podcast Subscribe Buttons'),
        ),
    ]