from django.core.management.base import BaseCommand
from models import ArticlePage
from tasks import generate_tts_for_page


class Command(BaseCommand):
    help = 'Generate TTS for all articles with tts_enabled'

    def handle(self, *args, **opts):
        qs = ArticlePage.objects.live().filter(tts_enabled=True)
        for page in qs:
            generate_tts_for_page.delay(page.id)
            self.stdout.write(self.style.SUCCESS(f'Queued TTS: {page.title}'))
