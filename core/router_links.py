"""Deep links from topic pills into a theme page's faceted listing.

A topic pill on a card (or in the expert hero's expertise row) links to the
theme page the topic belongs to — ``TopicPage.program_theme`` — with that topic
pre-selected in the theme page's resource listing (sync 2026-09-21; supersedes
the 2026-09-10 per-content-type router landing pages, whose setting is retired).
A topic with no theme, or a theme page with no resource listing yet, yields
``None`` and the pill renders plain — mapping topics to themes and placing the
listing are content steps, not deploys.

The link targets the FIRST faceted listing on the theme page whose card type
is a resource listing — top-level, or inside a composable Tabs panel (then
``?tab=<slug>`` is added so the right panel opens). Router params are
namespaced by the module's prefix (decision D2), so the URL is
``<path>?tab=<slug>&<prefix>-topic=<topic id>#router-<prefix>``.

Resolution is cached per process for ``CACHE_SECONDS`` (theme page bodies
change rarely); the cache also clears on any page publish/unpublish in the
worker that saw the signal. The TTL bounds staleness in the other workers.
"""

import time

from django.dispatch import receiver
from django.utils.http import urlencode
from wagtail.signals import page_published, page_unpublished

from core.faceted_listing import default_listing_prefix

# Faceted-listing card types a topic pill can land on: the theme-scoped
# resource listings, which read a ``<prefix>-topic`` param.
RESOURCE_CARD_TYPES = ('resource', 'resource-visual')

CACHE_SECONDS = 60

_targets = {}       # theme page id → (expires_at, (path, prefix, tab_slug) | None)


def clear_cache(**kwargs):
    _targets.clear()


def _listing_target(landing):
    """(path, prefix, tab_slug) of the first resource listing on ``landing``;
    ``None`` when the page carries no such module."""
    from streams.blocks import _slugify_label
    body = getattr(landing.specific, 'body', None)
    if body is None:
        return None
    parts = landing.get_url_parts()
    path = parts[2] if parts else landing.url

    def match(value):
        return (value.get('card_type') or 'resource') in RESOURCE_CARD_TYPES

    for child in body.raw_data:
        if child.get('type') == 'faceted_listing' and match(child['value']):
            v = child['value']
            return path, v.get('prefix') or default_listing_prefix(v), None
        if child.get('type') == 'composable_tabs':
            used = set()
            for tab in child['value'].get('tabs') or []:
                tab_value = tab.get('value') or tab
                slug = _slugify_label(tab_value.get('label'), used)
                for inner in tab_value.get('content') or []:
                    if inner.get('type') == 'faceted_listing' and match(inner['value']):
                        v = inner['value']
                        return path, v.get('prefix') or default_listing_prefix(v), slug
    return None


def theme_target(theme):
    """Cached (path, prefix, tab_slug) for a ``ThemePage``, or ``None``."""
    if theme is None or not getattr(theme, 'live', False):
        return None
    hit = _targets.get(theme.id)
    if hit is None or hit[0] < time.monotonic():
        _targets[theme.id] = (time.monotonic() + CACHE_SECONDS, _listing_target(theme))
    return _targets[theme.id][1]


def topic_theme_url(topic):
    """URL of the topic's theme page with ``topic`` pre-selected in the theme's
    resource listing, or ``None`` (no theme, or no listing on the theme page).
    Pass a topic fetched with ``select_related('program_theme')``."""
    target = theme_target(getattr(topic, 'program_theme', None))
    if not target:
        return None
    path, prefix, tab_slug = target
    params = []
    if tab_slug:
        params.append(('tab', tab_slug))
    params.append(('%s-topic' % prefix, topic.id))
    # The fragment is the router's anchor (faceted_listing_block.html renders
    # id="router-<prefix>"); router.js scrolls to it on load so the visitor
    # lands on the filtered results, not the page top (Evan).
    return '%s?%s#router-%s' % (path, urlencode(params), prefix)


@receiver(page_published)
@receiver(page_unpublished)
def _page_changed(**kwargs):
    clear_cache()
