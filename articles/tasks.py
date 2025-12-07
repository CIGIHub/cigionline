from django.utils import timezone
from django.core.files.base import ContentFile
from .tts import synthesize_plain_with_title_pause
from .models import ArticlePage


def generate_tts_for_page(page_id):
    # 1. Update the live page row
    try:
        article_page = ArticlePage.objects.get(pk=page_id)
    except ArticlePage.DoesNotExist:
        return

    page = article_page.get_latest_revision().as_object()
    text = page.get_plaintext()
    if not text:
        return

    audio_bytes = synthesize_plain_with_title_pause(
        page,
        voice_id=page.tts_voice,
        title_pause_ms=getattr(page, "tts_title_pause_ms", 800),
    )

    if not audio_bytes:
        return

    timestamp_int = int(timezone.now().timestamp())
    filename = f"article-{page.id}-{timestamp_int}.mp3"

    page.audio_file.save(filename, ContentFile(audio_bytes), save=False)
    page.tts_last_generated = timezone.now()
    page.save(update_fields=["audio_file", "tts_last_generated"])

    after_name = getattr(page.audio_file, "name", None)

    # 2. If the page has an unpublished draft, keep its latest revision in sync too
    if getattr(page, "has_unpublished_changes", False):
        latest_revision = page.get_latest_revision()
        if latest_revision and getattr(latest_revision, "content", None) is not None:
            content = latest_revision.content
            content["audio_file"] = after_name
            latest_revision.content = content
            latest_revision.save()
