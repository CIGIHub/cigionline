from articles.models import ArticlePage
from datetime import datetime
from django.core.management.base import BaseCommand
from events.models import EventPage
from multimedia.models import MultimediaPage
from publications.models import PublicationPage
from pathlib import Path

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

        print(f'Starting... {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

        article_count = ArticlePage.objects.count()
        print(f'Generating image renditions for {article_count} articles')
        for i in range((article_count // batch_limit) + 1):
            articles = ArticlePage.objects.all().order_by('id')[i * batch_limit:(i * batch_limit) + batch_limit]
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

        event_count = EventPage.objects.count()
        print(f'Generating image renditions for {event_count} events')
        for i in range((event_count // batch_limit) + 1):
            events = EventPage.objects.all().order_by('id')[i * batch_limit:(i * batch_limit) + batch_limit]
            for event in events:
                print(f'Event {event.id}: Starting')
                if event.image_social:
                    print(f'Event {event.id}: Generating og image from image_social')
                    event.image_social.get_rendition('fill-1600x900')
                elif event.image_hero and Path(event.image_hero.file.url) != '.gif':
                    print(f'Event {event.id}: Generating og image from image_hero')
                    event.image_hero.get_rendition('fill-1600x900')
                if event.image_hero and Path(event.image_hero.file.url) != '.gif':
                    print(f'Event {event.id}: Generating hero image')
                    event.image_hero.get_rendition('width-1280')
                print(f'Event {event.id}: Finished')

        multimedia_count = MultimediaPage.objects.count()
        print(f'Generating image renditions for {multimedia_count} multimedia')
        for i in range((multimedia_count // batch_limit) + 1):
            multimedia_pages = MultimediaPage.objects.all().order_by('id')[i * batch_limit:(i * batch_limit) + batch_limit]
            for multimedia in multimedia_pages:
                print(f'Multimedia {multimedia.id}: Starting')
                if multimedia.image_social:
                    print(f'Multimedia {multimedia.id}: Generating og image from image_social')
                    multimedia.image_social.get_rendition('fill-1600x900')
                elif multimedia.image_hero and Path(multimedia.image_hero.file.url) != '.gif':
                    print(f'Multimedia {multimedia.id}: Generating og image from image_hero')
                    multimedia.image_hero.get_rendition('fill-1600x900')
                if multimedia.image_feature and Path(multimedia.image_feature.file.url) != '.gif':
                    print(f'Multimedia {multimedia.id}: Generating medium feature image from image_feature')
                    multimedia.image_feature.get_rendition('fill-520x390')
                    print(f'Multimedia {multimedia.id}: Generating large feature image from image_feature')
                    multimedia.image_feature.get_rendition('fill-1440x990')
                elif multimedia.image_hero and Path(multimedia.image_hero.file.url) != '.gif':
                    print(f'Multimedia {multimedia.id}: Generating medium feature image from image_hero')
                    multimedia.image_hero.get_rendition('fill-520x390')
                    print(f'Multimedia {multimedia.id}: Generating large feature image from image_hero')
                    multimedia.image_hero.get_rendition('fill-1440x990')
                print(f'Multimedia {multimedia.id}: Finished')

        publication_count = PublicationPage.objects.count()
        print(f'Generating image renditions for {publication_count} publications')
        for i in range((publication_count // batch_limit) + 1):
            publications = PublicationPage.objects.all().order_by('id')[i * batch_limit:(i * batch_limit) + batch_limit]
            for publication in publications:
                print(f'Publication {publication.id}: Starting')
                if publication.image_social:
                    print(f'Publication {publication.id}: Generating og image from image_social')
                    publication.image_social.get_rendition('fill-1600x900')
                elif publication.image_hero and Path(publication.image_hero.file.url) != '.gif':
                    print(f'Publication {publication.id}: Generating og image from image_hero')
                    publication.image_hero.get_rendition('fill-1600x900')
                if publication.image_cover:
                    print(f'Publication {publication.id}: Generating cover image')
                    publication.image_cover.get_rendition('fill-600x900')
                if publication.image_feature and Path(publication.image_feature.file.url) != '.gif':
                    print(f'Publication {publication.id}: Generating medium feature image from image_feature')
                    publication.image_feature.get_rendition('fill-520x390')
                    print(f'Publication {publication.id}: Generating large feature image from image_feature')
                    publication.image_feature.get_rendition('fill-1440x990')
                elif publication.image_hero and Path(publication.image_hero.file.url) != '.gif':
                    print(f'Publication {publication.id}: Generating medium feature image from image_hero')
                    publication.image_hero.get_rendition('fill-520x390')
                    print(f'Publication {publication.id}: Generating large feature image from image_hero')
                    publication.image_hero.get_rendition('fill-1440x990')
                print(f'Publication {publication.id}: Finished')

        print(f'Finished... {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
