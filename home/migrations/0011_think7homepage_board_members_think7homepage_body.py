# Generated by Django 5.0.6 on 2024-10-29 18:53

import streams.blocks
import wagtail.blocks
import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_think7homepage'),
    ]

    operations = [
        migrations.AddField(
            model_name='think7homepage',
            name='board_members',
            field=wagtail.fields.StreamField([('board_members', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('bio_source_field', wagtail.blocks.ChoiceBlock(choices=[('full_bio', 'Full Biography'), ('short_bio', 'Short Biography')], help_text="Select the field from the person's page to populate their biography in this block. Default to 'Full Biography'.", max_choices=1, required=False, verbose_name='Biography Source Field')), ('persons', wagtail.blocks.StreamBlock([('person', wagtail.blocks.PageChooserBlock(page_type=['people.PersonPage'], required=True))], required=True))]))], blank=True),
        ),
        migrations.AddField(
            model_name='think7homepage',
            name='body',
            field=wagtail.fields.StreamField([('paragraph', streams.blocks.ParagraphBlock())], blank=True),
        ),
    ]
