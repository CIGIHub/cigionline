# Generated by Django 3.2.13 on 2022-07-13 14:36

from django.db import migrations, models
import streams.blocks
import wagtail.contrib.forms.models
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactformfield',
            name='choices',
            field=models.TextField(blank=True, help_text='Comma or new line separated list of choices. Only applicable in checkboxes, radio and dropdown.', verbose_name='choices'),
        ),
        migrations.AlterField(
            model_name='contactformfield',
            name='default_value',
            field=models.TextField(blank=True, help_text='Default value. Comma or new line separated values supported for checkboxes.', verbose_name='default value'),
        ),
        migrations.AlterField(
            model_name='contactpage',
            name='events_contact',
            field=wagtail.fields.StreamField([('contact_email', streams.blocks.ContactEmailBlock()), ('contact_person', streams.blocks.ContactPersonBlock(page_type=['people.PersonPage']))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='contactpage',
            name='from_address',
            field=models.EmailField(blank=True, max_length=255, verbose_name='from address'),
        ),
        migrations.AlterField(
            model_name='contactpage',
            name='human_resources_contact',
            field=wagtail.fields.StreamField([('contact_email', streams.blocks.ContactEmailBlock()), ('contact_person', streams.blocks.ContactPersonBlock(page_type=['people.PersonPage']))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='contactpage',
            name='media_contact',
            field=wagtail.fields.StreamField([('contact_email', streams.blocks.ContactEmailBlock()), ('contact_person', streams.blocks.ContactPersonBlock(page_type=['people.PersonPage']))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='contactpage',
            name='to_address',
            field=models.CharField(blank=True, help_text='Optional - form submissions will be emailed to these addresses. Separate multiple addresses by comma.', max_length=255, validators=[wagtail.contrib.forms.models.validate_to_address], verbose_name='to address'),
        ),
    ]
