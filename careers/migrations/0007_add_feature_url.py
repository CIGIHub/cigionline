# Generated by Django 3.2.4 on 2021-12-15 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careers', '0006_jobpostingpage_search_result_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobpostingpage',
            name='feature_url',
            field=models.URLField(blank=True),
        ),
    ]
