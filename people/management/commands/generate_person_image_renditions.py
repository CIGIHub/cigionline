from datetime import datetime
from django.core.management.base import BaseCommand
from people.models import PersonPage


class Command(BaseCommand):
    def handle(self, ** options):
        batch_limit = 50

        print(f'Starting... {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

        person_count = PersonPage.objects.live().count()
        if person_count > 1000:
            person_count = 1000
        print(f'Generating image renditions for {person_count} people')
        for i in range((person_count // batch_limit) + 1):
            people = PersonPage.objects.live().order_by('-id')[i * batch_limit:(i * batch_limit) + batch_limit]
            for person in people:
                print(f'Person {person.id}: Starting')
                if person.image_media:
                    print(f'Person {person.id}: Generating og image from image_media')
                    person.image_media.get_rendition('fill-1600x900')
                if person.image_square:
                    print(f'Person {person.id}: Generating square image for expert page')
                    person.image_square.get_rendition('fill-200x200')
                    print(f'Person {person.id}: Generating square image for experts landing page')
                    person.image_square.get_rendition('fill-300x300')
                    print(f'Person {person.id}: Generating feature expert image')
                    person.image_square.get_rendition('fill-140x140')
                print(f'Person {person.id}: Finished')

        print(f'Finished... {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
