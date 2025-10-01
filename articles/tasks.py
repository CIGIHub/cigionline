from celery import shared_task
from django.utils import timezone
from django.core.files.base import ContentFile
from .tts import synthesize_full_mp3
from .models import ArticlePage


# @shared_task
# def generate_tts_for_page_async(page_id):
#     page = ArticlePage.objects.filter(id=page_id).specific().first()
#     if not page or not page.tts_enabled:
#         return
#     text = page.get_plaintext()
#     if not text:
#         return
#     audio_bytes = synthesize_full_mp3(text, voice_id=page.tts_voice, use_ssml=False)
#     filename = f'article-{page.id}-{int(timezone.now().timestamp())}.mp3'
#     page.audio_file.save(filename, ContentFile(audio_bytes), save=False)
#     page.tts_last_generated = timezone.now()
#     page.save()


@shared_task
def generate_tts_for_page_sync(page_id):
    print("Generating TTS for page", page_id)
    page = ArticlePage.objects.filter(id=page_id).specific().first()
    if not page or not page.tts_enabled:
        return
    text = page.get_plaintext()
    if not text:
        return
    audio_bytes = synthesize_full_mp3(text, voice_id=page.tts_voice, use_ssml=False)
    filename = f"article-{page.id}-{int(timezone.now().timestamp())}.mp3"
    page.audio_file.save(filename, ContentFile(audio_bytes), save=False)
    page.tts_last_generated = timezone.now()
    page.save()
