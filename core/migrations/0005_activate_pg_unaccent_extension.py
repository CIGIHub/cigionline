# Generated by Django 3.1.5 on 2021-01-17 19:02

from django.contrib.postgres.operations import UnaccentExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_populate_themes'),
    ]

    operations = [
        UnaccentExtension(),
    ]
