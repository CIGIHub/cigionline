from django.core.management.base import BaseCommand
from articles.models import ArticleSeriesPage


class Command(BaseCommand):
    help = 'Takes ArticleSeriesPage id and publishes all articles featured on the series page'

    def add_arguments(self, parser):
        parser.add_argument('series_id', nargs='+', type=int)

    def handle(self, *args, **options):
        article_series_page = ArticleSeriesPage.objects.get(id=options['series_id'][0])
        for page in article_series_page.article_series_items:
            try:
                page.content_page.specific.get_latest_revision().publish()
                for author in page.content_page.authors.all():
                    try:
                        author.author.get_latest_revision().publish()
                        print(f'Published Author "{author.author.title}" successfully')
                    except Exception:
                        print(f'Error: Author "{author.author.title}" was not published')
                print(f'Published {page.content_page.contenttype} - {page.content_page.title} successfully')
            except Exception:
                print(f'Error: {page.content_page.contenttype} - {page.content_page.title} was not published')

        article_series_page.get_latest_revision().publish()
