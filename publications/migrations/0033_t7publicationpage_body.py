# Generated by Django 5.0.6 on 2025-04-28 20:08

import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0032_publicationlistpage_t7_communiques'),
    ]

    operations = [
        migrations.AddField(
            model_name='t7publicationpage',
            name='body',
            field=wagtail.fields.RichTextField(blank=True, null=True),
        ),
    ]
