# Generated by Django 3.2.4 on 2021-12-15 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0007_publicationpage_ctas'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicationpage',
            name='feature_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='publicationseriespage',
            name='feature_url',
            field=models.URLField(blank=True),
        ),
    ]
