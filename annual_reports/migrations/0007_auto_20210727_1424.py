# Generated by Django 3.2.4 on 2021-07-27 18:24

from django.db import migrations, models
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('annual_reports', '0006_use_custom_image_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='annualreportlistpage',
            name='search_result_description',
            field=models.CharField(blank=True, help_text='Text that is displayed when this page appears in search results', max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name='annualreportlistpage',
            name='search_terms',
            field=wagtail.fields.StreamField([('search_term', wagtail.blocks.CharBlock())], blank=True, help_text='A list of search terms for which this page will be elevated in the search results.'),
        ),
        migrations.AddField(
            model_name='annualreportpage',
            name='search_result_description',
            field=models.CharField(blank=True, help_text='Text that is displayed when this page appears in search results', max_length=1024, null=True),
        ),
    ]
