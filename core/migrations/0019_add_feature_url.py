# Generated by Django 3.2.4 on 2021-12-15 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20210727_1424'),
    ]

    operations = [
        migrations.AddField(
            model_name='basicpage',
            name='feature_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='twentiethpage',
            name='feature_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='twentiethpagesingleton',
            name='feature_url',
            field=models.URLField(blank=True),
        ),
    ]
