# Generated by Django 3.2.13 on 2022-08-12 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0007_personpage_search_result_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='personpage',
            name='exclude_from_search',
            field=models.BooleanField(default=False),
        ),
    ]
