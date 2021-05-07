from articles.models import ArticleSeriesPage
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import models
from pathlib import Path


class Command(BaseCommand):
    def handle(self, ** options):
        batch_limit = 50

        print(f'Starting... {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

        article_series_count = ArticleSeriesPage.objects.live().count()
        if article_series_count > 1000:
            article_series_count = 1000
        print(f'Generating image renditions for {article_series_count} article series')
        for i in range((article_series_count // batch_limit) + 1):
            article_series_pages = ArticleSeriesPage.objects.live().order_by(models.F('publishing_date').desc(nulls_last=True))[i * batch_limit:(i * batch_limit) + batch_limit]
            for article_series in article_series_pages:
                print(f'Article Series {article_series.id}: Starting')
                if article_series.image_feature and Path(article_series.image_feature.file.url) != '.gif':
                    print(f'Article Series {article_series.id}: Generating medium feature image from image_feature')
                    article_series.image_feature.get_rendition('fill-520x390')
                    print(f'Article Series {article_series.id}: Generating large feature image from image_feature')
                    article_series.image_feature.get_rendition('fill-1440x990')
                elif article_series.image_hero and Path(article_series.image_hero.file.url) != '.gif':
                    print(f'Article Series {article_series.id}: Generating medium feature image from image_hero')
                    article_series.image_hero.get_rendition('fill-520x390')
                    print(f'Article Series {article_series.id}: Generating large feature image from image_hero')
                    article_series.image_hero.get_rendition('fill-1440x990')
                if article_series.image_poster and Path(article_series.image_poster.file.url) != '.gif':
                    print(f'Article Series {article_series.id}: Generating poster image')
                    article_series.image_poster.get_rendition('width-700')
                print(f'Article Series {article_series.id}: Finished')

        print(f'Finished... {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
