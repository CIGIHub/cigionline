# Generated by Django 3.2.4 on 2022-01-19 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0016_articleseriespage_series_items_disclaimer'),
    ]

    operations = [
        migrations.AddField(
            model_name='articleseriespageseriesitem',
            name='hide_series_disclaimer',
            field=models.BooleanField(default=False),
        ),
    ]
