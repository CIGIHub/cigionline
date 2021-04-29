from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import models
from events.models import EventPage
from pathlib import Path


class Command(BaseCommand):
    def handle(self, ** options):
        batch_limit = 50

        print(f'Starting... {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

        event_count = EventPage.objects.live().count()
        if event_count > 1000:
            event_count = 1000
        print(f'Generating image renditions for {event_count} events')
        for i in range((event_count // batch_limit) + 1):
            events = EventPage.objects.live().order_by(models.F('publishing_date').desc(nulls_last=True))[i * batch_limit:(i * batch_limit) + batch_limit]
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

        print(f'Finished... {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
