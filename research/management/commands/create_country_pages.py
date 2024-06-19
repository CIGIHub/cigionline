from django.core.management.base import BaseCommand
from research.models import CountryPage, CountryListPage
from utils.helpers import CreatePage, CreateCountryPage
from iso3166 import countries


class Command(BaseCommand):
    def handle(self, *args, **options):
        CreatePage(
            page_model=CountryListPage,
            page_title='Countries',
            parent_page_title='Home'
        ).create_page()

        for country in countries:
            print(f'Creating page for {country.name}...')
            CreateCountryPage(
                page_model=CountryPage,
                page_title=country.name,
                parent_page_title='Countries',
                country_iso=country
            ).create_country_page()
