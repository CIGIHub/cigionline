# Generated by Django 5.0.6 on 2024-10-31 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0044_remove_projectpage_primary_theme_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectpage',
            name='task_force_label',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
