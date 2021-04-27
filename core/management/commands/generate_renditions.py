from articles.models import ArticlePage
from django.core.management.base import BaseCommand
from pathlib import Path
# from wagtail.images import get_image_model

RENDITIONS = [
    'fill-1600x900',  # og
    'original',
    'width-300',
    'fill-100x100',
    'fill-377x246',
    'width-1760',  # hero - article
    'width-640',
    'width-700',
    'fill-600x238',
    'fill-672x895',
    'width-100',
    'width-600',
    # These rendition types are used in 2 or fewer templates
    # skipped to speed up the process
    # 'fill-1440x990',
    # 'width-1280',
    # 'width-1440',
    # 'width-500',
    # 'fill-140x140',
    # 'fill-150x150',
    # 'fill-200x200',
    # 'fill-520x390',
    # 'fill-600x600',
    # 'fill-600x900',
    # 'max-450x200',
    # 'width-1024',
    # 'width-1920',
    # 'width-200',
    # 'width-768',
]


class Command(BaseCommand):

    def handle(self, **options):
        batch_limit = 50
        article_count = ArticlePage.objects.count()
        print(f'Generating image renditions for {article_count} articles')
        for i in range((article_count // batch_limit) + 1):
            articles = ArticlePage.objects.all().order_by('id')[i * 50:(i * 50) + 50]
            for article in articles:
                print(f'Article {article.id}: Starting')
                if article.image_social:
                    print(f'Article: {article.id}: Generating og image from image_social')
                    article.image_social.get_rendition('fill-1600x900')
                elif article.image_hero and Path(article.image_hero.file.url) != '.gif':
                    print(f'Article: {article.id}: Generating og image from image_hero')
                    article.image_hero.get_rendition('fill-1600x900')
                if article.image_hero and Path(article.image_hero.file.url) != '.gif':
                    print(f'Article: {article.id}: Generating hero image')
                    article.image_hero.get_rendition('width-1760')
                if article.image_feature and Path(article.image_feature.file.url) != '.gif':
                    print(f'Article: {article.id}: Generating medium feature image from image_feature')
                    article.image_feature.get_rendition('fill-520x390')
                    print(f'Article: {article.id}: Generating large feature image from image_feature')
                    article.image_feature.get_rendition('fill-1440x990')
                elif article.image_hero and Path(article.image_hero.file.url) != '.gif':
                    print(f'Article: {article.id}: Generating medium feature image from image_hero')
                    article.image_hero.get_rendition('fill-520x390')
                    print(f'Article: {article.id}: Generating large feature image from image_hero')
                    article.image_hero.get_rendition('fill-1440x990')
                print(f'Article {article.id}: Finished')

        # Image = get_image_model()
        # images = Image.objects.all()
        # print(f"Generating renditions for {images.count()} images...")
        # for image in images:
        #     for rendition in RENDITIONS:
        #         try:
        #             image.get_rendition(rendition)
        #         except Exception:
        #             pass
