# Generated by Django 3.2.18 on 2023-09-05 17:09

from django.db import migrations
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0012_alter_person_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='personpage',
            name='short_description',
            field=wagtail.fields.RichTextField(blank=True),
        ),
    ]