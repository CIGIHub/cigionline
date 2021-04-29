from articles.models import ArticlePage
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import models
from pathlib import Path


class Command(BaseCommand):
    def handle(self, ** options):
        batch_limit = 50

        print(f'Starting... {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

        article_count = ArticlePage.objects.live().count()
        if article_count > 1000:
            article_count = 1000
        print(f'Generating image renditinos for {article_count} articles')
        for i in range((article_count // batch_limit) + 1):
            articles = ArticlePage.objects.live().order_by(models.F('publishing_date').desc(nulls_last=True))[i * batch_limit:(i * batch_limit) + batch_limit]
            for article in articles:
                print(f'Article {article.id}: Starting')
                if article.image_social:
                    print(f'Article {article.id}: Generating og image from image_social')
                    article.image_social.get_rendition('fill-1600x900')
                elif article.image_hero and Path(article.image_hero.file.url) != '.gif':
                    print(f'Article {article.id}: Generating og image from image_hero')
                    article.image_hero.get_rendition('fill-1600x900')
                if article.image_hero and Path(article.image_hero.file.url) != '.gif':
                    print(f'Article {article.id}: Generating hero image')
                    article.image_hero.get_rendition('width-1760')
                if article.image_feature and Path(article.image_feature.file.url) != '.gif':
                    print(f'Article {article.id}: Generating medium feature image from image_feature')
                    article.image_feature.get_rendition('fill-520x390')
                    print(f'Article {article.id}: Generating large feature image from image_feature')
                    article.image_feature.get_rendition('fill-1440x990')
                    print(f'Article {article.id}: Generating recommended block image from image_feature')
                    article.image_feature.get_rendition('fill-377x246')
                    print(f'Article {article.id}: Generating multimedia recommended image from image_feature')
                    article.image_feature.get_rendition('width-300')
                elif article.image_hero and Path(article.image_hero.file.url) != '.gif':
                    print(f'Article {article.id}: Generating medium feature image from image_hero')
                    article.image_hero.get_rendition('fill-520x390')
                    print(f'Article {article.id}: Generating large feature image from image_hero')
                    article.image_hero.get_rendition('fill-1440x990')
                    print(f'Article {article.id}: Generating recommended block image from image_hero')
                    article.image_hero.get_rendition('fill-377x246')
                    print(f'Article {article.id}: Generating multimedia recommended image from image_hero')
                    article.image_hero.get_rendition('width-300')
                for block in article.body:
                    if (block.block_type == 'image' or block.block_type == 'chart') and block.value['image'] is not None:
                        print(f'Article {article.id} Generating image for ImageBlock')
                        block.value['image'].get_rendition('width-640')
                print(f'Article {article.id}: Finished')

        print(f'Finished... {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
