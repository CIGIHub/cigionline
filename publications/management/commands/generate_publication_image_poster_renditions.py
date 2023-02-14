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
                if publication.image_cover:
                    print(f'Publication {publication.id}: Generating cover image')
                    publication.image_cover.get_rendition('fill-525x700')
                if publication.image_poster and Path(publication.image_poster.file.url) != '.gif':
                    print(f'Publication {publication.id}: Generating poster image')
                    publication.image_poster.get_rendition('fill-525x700')
                print(f'Publication {publication.id}: Finished')

        print(f'Finished... {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
