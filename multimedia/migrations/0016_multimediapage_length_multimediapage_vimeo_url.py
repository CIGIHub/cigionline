# Generated by Django 4.0 on 2023-06-12 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0015_multimediapage_short_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='multimediapage',
            name='length',
            field=models.CharField(blank=True, help_text='| CIGI 3.0 field | The length of the multimedia source in minutes and seconds (e.g. 1:23).', max_length=8, verbose_name='Length'),
        ),
        migrations.AddField(
            model_name='multimediapage',
            name='vimeo_url',
            field=models.URLField(blank=True, help_text='| CIGI 3.0 field | The URL of the multimedia source from Vimeo.', verbose_name='Vimeo URL'),
        ),
    ]