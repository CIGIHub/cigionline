# Generated by Django 3.2.4 on 2022-04-26 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0018_articleseriespage_series_videos_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlepage',
            name='feature_subtitle',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='articleseriespage',
            name='feature_subtitle',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
