from django.db import migrations
from research.models import CountryPage, CountryListPage
from utils.helpers import CreatePage, CreateCountryPage
from iso3166 import countries


def create_country_list_page(apps, schema_editor):
    CreatePage(
        page_model=CountryListPage,
        page_title='Countries',
        parent_page_title='Home'
    ).create_page()


def create_country_pages(apps, schema_editor):
    for country in countries:
        CreateCountryPage(
            page_model=CountryPage,
            page_title=country.name,
            parent_page_title='Countries',
            country_iso=country
        ).create_country_page()


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0041_countrylistpage_countrypage'),
    ]

    operations = [
        migrations.RunPython(create_country_list_page),
        migrations.RunPython(create_country_pages),
    ]
