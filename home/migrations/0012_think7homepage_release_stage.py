# Generated by Django 5.0.6 on 2024-11-05 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0011_think7homepage_board_members_think7homepage_body'),
    ]

    operations = [
        migrations.AddField(
            model_name='think7homepage',
            name='release_stage',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
