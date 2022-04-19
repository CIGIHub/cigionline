from django.core.management.base import BaseCommand
from articles.models import ArticleSeriesPage


class Command(BaseCommand):
    help = 'Takes ArticleSeriesPage id and publishes all articles featured on the series page'

    def add_arguments(self, parser):
        parser.add_argument('series_id', nargs='+', type=int)

    def handle(self, *args, **options):
        article_series_page = ArticleSeriesPage.objects.get(id=options['series_id'][0])
        for page in article_series_page.article_series_items:
            page.content_page.specific.save_revision().publish()
