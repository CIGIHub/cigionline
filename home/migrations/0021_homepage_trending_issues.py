# Generated by Django 4.0 on 2023-03-08 18:21

from django.db import migrations
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0020_alter_homepage_layout'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='trending_issues',
            field=wagtail.fields.StreamField([('issue', wagtail.blocks.PageChooserBlock(page_type=['research.IssuePage'], required=False))], blank=True, use_json_field=True),
        ),
    ]
