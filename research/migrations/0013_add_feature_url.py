# Generated by Django 3.2.4 on 2021-12-15 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0012_projectpage_image_banner'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectpage',
            name='feature_url',
            field=models.URLField(blank=True),
        ),
    ]
