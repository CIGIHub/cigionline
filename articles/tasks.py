from celery import shared_task
from django.utils import timezone
from django.core.files.base import ContentFile
from .tts import synthesize_plain_with_title_pause
from .models import ArticlePage


@shared_task
def generate_tts_for_page(page_id):
    page = ArticlePage.objects.filter(id=page_id).specific().first()
    if page and page.tts_enabled:
        text = page.get_plaintext()
        if text:
            audio_bytes = synthesize_plain_with_title_pause(
                page,
                voice_id=page.tts_voice,
                title_pause_ms=getattr(page, 'tts_title_pause_ms', 800)
            )
            filename = f"article-{page.id}-{int(timezone.now().timestamp())}.mp3"
            page.audio_file.save(filename, ContentFile(audio_bytes), save=False)
            page.tts_last_generated = timezone.now()
            page.save()
