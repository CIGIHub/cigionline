from django.core.cache import cache
from wagtail.core.management.commands import publish_scheduled_pages

class Command(publish_scheduled_pages.Command):
    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)

        cache.delete((cache.keys('*homepage_featured_content*'))[0])