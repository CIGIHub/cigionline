# Generated by Django 3.2.18 on 2024-03-21 14:54

from django.db import migrations
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0040_rename_old_opinion_series_to_essay_series'),
    ]

    operations = [
        migrations.AddField(
            model_name='opinionseriespage',
            name='series_items_description',
            field=wagtail.fields.RichTextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='opinionseriespage',
            name='series_items_disclaimer',
            field=wagtail.fields.RichTextField(blank=True, null=True),
        ),
    ]