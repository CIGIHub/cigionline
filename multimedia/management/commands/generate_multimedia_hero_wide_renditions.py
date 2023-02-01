from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import models
from multimedia.models import MultimediaPage
from pathlib import Path


class Command(BaseCommand):
    def handle(self, ** options):
        batch_limit = 50

        print(f'Starting... {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

        multimedia_count = MultimediaPage.objects.live().count()
        if multimedia_count > 1000:
            multimedia_count = 1000
        print(f'Generating hero image wide renditions for {multimedia_count} multimedia')
        for i in range((multimedia_count // batch_limit) + 1):
            multimedia_pages = MultimediaPage.objects.live().order_by(models.F('publishing_date').desc(nulls_last=True))[i * batch_limit:(i * batch_limit) + batch_limit]
            for multimedia in multimedia_pages:
                print(f'Multimedia {multimedia.id}: Starting')
                if multimedia.image_feature and Path(multimedia.image_feature.file.url) != '.gif':
                    print(f'Multimedia {multimedia.id}: Generating medium wide feature image from image_feature')
                    multimedia.image_feature.get_rendition('fill-600x300')
                elif multimedia.image_hero and Path(multimedia.image_hero.file.url) != '.gif':
                    print(f'Multimedia {multimedia.id}: Generating medium wide feature image from image_hero')
                    multimedia.image_hero.get_rendition('fill-600x300')
                print(f'Multimedia {multimedia.id}: Finished')

        print(f'Finished... {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
