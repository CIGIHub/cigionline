"""Materialize each expert's derived expertise tags.

An expert's expertise = the distinct *active* (live, non-archived) topics across
the live content they've authored. Computing that per-card risks flaky queries on
dense pages, so it's materialized into `PersonPage.derived_topics` here and read
cheaply by `expert_data`. Idempotent; safe to re-run. Wired to a weekly cron (no
Celery in this project — same pattern as send_scheduled_event_emails).

One grouped query collects every (author, topic) edge; we then bulk `.set()` per
author — a handful of queries total regardless of expert count. `derived_topics`
is a plain (non-Parental) M2M, so `.set()` persists without a page save and does
NOT touch the curated `person.topics` (which drives the experts search facet).
"""
from collections import defaultdict

from django.core.cache import cache
from django.core.management.base import BaseCommand

from core.models import ContentPageAuthor
from people.models import PersonPage


class Command(BaseCommand):
    help = "Recompute PersonPage.derived_topics from authored live content."

    def handle(self, *args, **options):
        # (author_id, topic_id) for every live-content / active-topic edge.
        edges = (ContentPageAuthor.objects
                 .filter(content_page__live=True,
                         content_page__topics__archive=0,
                         content_page__topics__live=True)
                 .values_list('author_id', 'content_page__topics')
                 .distinct())

        topics_by_author = defaultdict(set)
        for author_id, topic_id in edges:
            if topic_id is not None:
                topics_by_author[author_id].add(topic_id)

        # Only touch people who have edges now, plus anyone who currently holds
        # derived tags (so removed/stale tags are cleared) — not every PersonPage.
        existing = set(PersonPage.objects
                       .filter(derived_topics__isnull=False)
                       .values_list('id', flat=True).distinct())
        to_process = set(topics_by_author) | existing

        people = PersonPage.objects.filter(id__in=to_process).only('id')
        updated = 0
        for person in people:
            person.derived_topics.set(topics_by_author.get(person.id, set()))
            updated += 1

        # Expert API responses embed expertise tags — drop their cache. delete_pattern
        # is a Redis extension; dev's DummyCache lacks it, so guard the call.
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern("*all_experts*")

        self.stdout.write(self.style.SUCCESS(
            f"Updated derived_topics for {updated} people "
            f"({len(topics_by_author)} with ≥1 derived topic)."
        ))
