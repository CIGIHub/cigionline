"""The archive page untagged content trails back to (BugHerd #279).

Content singles that no current program owns crumb "Home > <archive page>"
(IA decision 2026-09-04, CIGI aligned 2026-09-09: "HOME -> Archive ->
content"). The archive is whichever page carries the faceted listing in
"Archive — content with no program" mode (e441b25d). It is found, in order:

1. Settings -> Archive (``ArchiveSettings.archive_page``), when it points at a
   live, public page;
2. otherwise the oldest live, public BasicPage whose body has a top-level
   Faceted Listing with ``program_source='none'`` — no slug or title match,
   so CIGI can rename and move the page freely;
3. otherwise ``None``, and the hero keeps its tree trail.

The crumb label is the page's own title. Resolution is cached per process for
``CACHE_SECONDS`` (the same contract as ``core.router_links``): any page
publish, unpublish or move and any save of the setting clears it in the worker
that saw the signal; the TTL bounds staleness in the other workers. Only plain
values are cached, never ORM objects.
"""

import time

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from wagtail.signals import page_published, page_unpublished, post_page_move

CACHE_SECONDS = 60

_cache = {}         # 'target' → (expires_at, {'title', 'url'} | None)


def clear_cache(**kwargs):
    _cache.clear()


def _archive_page():
    from wagtail.models import Page
    from core.models import BasicPage
    from core.models_settings import ArchiveSettings

    chosen = ArchiveSettings.load().archive_page_id
    page = Page.objects.live().public().filter(pk=chosen).first() if chosen else None
    if page is None:
        # Oldest wins, so a later test copy of the archive can't take over.
        page = (BasicPage.objects.live().public()
                .filter(body__contains=[{'type': 'faceted_listing',
                                         'value': {'program_source': 'none'}}])
                .order_by('pk').first())
    return page


def archive_target():
    """Cached ``{'title', 'url'}`` of the archive page, or ``None``."""
    hit = _cache.get('target')
    if hit is None or hit[0] < time.monotonic():
        from core.heroes import _rel_url
        page = _archive_page()
        target = {'title': page.title, 'url': _rel_url(page)} if page else None
        _cache['target'] = hit = (time.monotonic() + CACHE_SECONDS, target)
    return hit[1]


@receiver(post_save, sender='core.ArchiveSettings')
@receiver(post_delete, sender='core.ArchiveSettings')
def _settings_changed(**kwargs):
    clear_cache()


@receiver(page_published)
@receiver(page_unpublished)
@receiver(post_page_move)
def _page_changed(**kwargs):
    clear_cache()
