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
                    print(f'Article Series {article_series.id}: Generating poster image for opinion series page')
                    article_series.image_poster.get_rendition('fill-672x895')
                if article_series.theme.name == 'Platform Governance Series':
                    print(f'Article Series {article_series.id}: Generating Platform Governance series banner image')
                    article_series.image_banner.get_rendition('width-1440')
                    print(f'Article Series {article_series.id}: Generating Platform Governance series small banner image')
                    article_series.image_banner.get_rendition('width-100')
                if article_series.theme.name == 'Indigenous Lands Series':
                    print(f'Article Series {article_series.id}: Generating Indigenous Lands series hero image')
                    article_series.image_hero.get_rendition('original')
                if article_series.theme.name == 'Cyber Series':
                    print(f'Article Series {article_series.id}: Generating Cyber series hero image')
                    article_series.image_hero.get_rendition('original')
                if article_series.theme.name == 'Longform':
                    print(f'Article Series {article_series.id}: Generating Longform banner image')
                    article_series.image_banner.get_rendition('original')
                if article_series.theme.name == 'Innovation Series':
                    print(f'Article Series {article_series.id}: Generating Innovation series hero image')
                    article_series.image_hero.get_rendition('original')
                for series_item in article_series.article_series_items:
                    if article_series.theme.name == 'AI Series':
                        if series_item.content_page.specific.image_banner:
                            print(f'Article Series {article_series.id}, {series_item.content_page.id}: Generating AI series in the series image')
                            series_item.content_page.specific.image_banner.get_rendition('max-450x200')
                            print(f'Article Series {article_series.id}, {series_item.content_page.id}: Generating AI series hero image')
                            series_item.content_page.specific.image_banner.get_rendition('original')
                    if article_series.theme.name == 'Health Security Series':
                        if series_item.content_page.specific.image_banner:
                            print(f'Article Series {article_series.id}, {series_item.content_page.id}: Generating Health Security series hero image')
                            series_item.content_page.specific.image_banner.get_rendition('original')
                    if article_series.theme.name == 'After-COVID Series':
                        if series_item.content_page.specific.image_banner:
                            print(f'Article Series {article_series.id}, {series_item.content_page.id}: Generating After-COVID series banner image')
                            series_item.content_page.specific.image_banner.get_rendition('original')
                        if series_item.content_page.specific.image_hero:
                            print(f'Article Series {article_series.id}, {series_item.content_page.id}: Generating After-COVID series hero image')
                            series_item.content_page.specific.image_hero.get_rendition('width-768')
                    if article_series.theme.name == 'Platform Governance Series':
                        if series_item.content_page.specific.image_banner:
                            print(f'Article Series {article_series.id}, {series_item.content_page.id}: Generating Platform Governance series banner image')
                            series_item.content_page.specific.image_banner.get_rendition('width-1440')
                            print(f'Article Series {article_series.id}, {series_item.content_page.id}: Generating Platform Governance series small banner image')
                            series_item.content_page.specific.image_banner.get_rendition('width-100')
                            print(f'Article Series {article_series.id}, {series_item.content_page.id}: Generating Platform Governance series in the series image')
                            series_item.content_page.specific.image_banner.get_rendition('fill-672x895')
                    if article_series.theme.name == 'Cyber Series':
                        if series_item.content_page.specific.image_banner:
                            print(f'Article Series {article_series.id}, {series_item.content_page.id}: Generating Cyber series banner image')
                            series_item.content_page.specific.image_banner.get_rendition('original')
                    if article_series.theme.name == 'Longform':
                        if series_item.content_page.specific.image_banner:
                            print(f'Article Series {article_series.id}, {series_item.content_page.id}: Generating Longform banner image')
                            series_item.content_page.specific.image_banner.get_rendition('original')
                        if series_item.content_page.specific.image_hero:
                            print(f'Article Series {article_series.id}, {series_item.content_page.id}: Generating Longform featured image')
                            series_item.content_page.specific.image_hero.get_rendition('original')
                    if article_series.theme.name == 'Data Series':
                        if series_item.content_page.specific.image_banner:
                            print(f'Article Series {article_series.id}, {series_item.content_page.id}: Generating Data series banner image')
                            series_item.content_page.specific.image_banner.get_rendition('original')
                    if article_series.theme.name == 'Innovation Series':
                        if series_item.content_page.specific.image_banner:
                            print(f'Article Series {article_series.id}, {series_item.content_page.id}: Generating Innovation series banner image')
                            series_item.content_page.specific.image_banner.get_rendition('original')
                        if series_item.content_page.specific.image_hero:
                            print(f'Article Series {article_series.id}, {series_item.content_page.id}: Generating Innovation series featured image')
                            series_item.content_page.specific.image_hero.get_rendition('original')
                        if hasattr(series_item.content_page.specific, 'image_banner_small') and series_item.content_page.specific.image_banner_small:
                            print(f'Article Series {article_series.id}, {series_item.content_page.id}: Generating Innovation series article background from image_banner_small')
                            series_item.content_page.specific.image_banner_small.get_rendition('original')
                        elif hasattr(series_item.content_page.specific, 'image_square') and series_item.content_page.specific.image_square:
                            print(f'Article Series {article_series.id}, {series_item.content_page.id}: Generating Innovation series article background from image_square')
                            series_item.content_page.specific.image_square.get_rendition('original')
                print(f'Article Series {article_series.id}: Finished')

        print(f'Finished... {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
