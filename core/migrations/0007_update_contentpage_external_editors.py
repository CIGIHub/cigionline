# Generated by Django 3.1.5 on 2021-01-19 23:36

from django.db import migrations
import streams.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_activate_pg_unaccent_extension'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentpage',
            name='external_editors',
            field=wagtail.core.fields.StreamField([('external_person', streams.blocks.ExternalPersonBlock())], blank=True),
        ),
    ]
