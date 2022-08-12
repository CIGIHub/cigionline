# Generated by Django 3.2.13 on 2022-08-12 15:34

from django.db import migrations, models
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20220812_1021'),
    ]

    operations = [
        migrations.AddField(
            model_name='privacynoticepage',
            name='exclude_from_search',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='privacynoticepage',
            name='search_result_description',
            field=models.CharField(blank=True, help_text='Text that is displayed when this page appears in search results', max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name='privacynoticepage',
            name='search_terms',
            field=wagtail.core.fields.StreamField([('search_term', wagtail.core.blocks.CharBlock())], blank=True, help_text='A list of search terms for which this page will be elevated in the search results.'),
        ),
    ]
