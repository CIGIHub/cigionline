"""Shared page-query helpers — DRY the repeated live/public/dated chains used by
the dynamic-module blocks (streams/blocks.py). Free functions (not a custom page
manager) so they work uniformly on model managers AND related managers
(e.g. ``program.content_pages``) without touching Wagtail's page-manager setup.
"""


def live_dated(queryset, require_date=True):
    """Live + public pages, newest first by ``publishing_date``.

    ``queryset`` is any Page queryset or related manager. Set
    ``require_date=False`` to keep undated pages. Chain ``.specific()`` /
    slicing after as the caller needs.
    """
    qs = queryset.live().public()
    if require_date:
        qs = qs.filter(publishing_date__isnull=False)
    return qs.order_by('-publishing_date')
