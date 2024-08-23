# Generated by Django 5.0.6 on 2024-08-09 13:45

import modelcluster.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0043_auto_20240709_1057'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectpage',
            name='primary_theme',
        ),
        migrations.AddField(
            model_name='projectpage',
            name='primary_themes',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, related_name='primary_themes', to='research.themepage'),
        ),
    ]