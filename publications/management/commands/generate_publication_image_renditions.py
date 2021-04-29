from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import models
from pathlib import Path
from publications.models import PublicationPage


class Command(BaseCommand):
    def handle(self, ** options):
        batch_limit = 50

        print(f'Starting... {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

        publication_count = PublicationPage.objects.live().count()
        if publication_count > 1000:
            publication_count = 1000
        print(f'Generating image renditions for {publication_count} publications')
        for i in range((publication_count // batch_limit) + 1):
            publications = PublicationPage.objects.live().order_by(models.F('publishing_date').desc(nulls_last=True))[i * batch_limit:(i * batch_limit) + batch_limit]
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
                if publication.image_poster and Path(publication.image_poster.file.url) != '.gif':
                    print(f'Publication {publication.id}: Generating poster image')
                    publication.image_poster.get_rendition('width-700')
                print(f'Publication {publication.id}: Finished')

        print(f'Finished... {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
