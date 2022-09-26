# Generated by Django 3.2.15 on 2022-09-26 17:38

from django.db import migrations
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_merge_0021_auto_20220713_1036_0022_auto_20220812_1134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='privacynoticepage',
            name='search_terms',
            field=wagtail.fields.StreamField([('search_term', wagtail.blocks.CharBlock())], blank=True, help_text='A list of search terms for which this page will be elevated in the search results.', use_json_field=True),
        ),
    ]
