"""Recreate the DS module QA test pages (the ``*-test`` articles) on any
environment — built for the staging module pass, where the local-only test
placements left ~19 modules unverifiable (close-out A.6 / qa-catalogue §2–4).

The bodies were exported verbatim from the local QA pages
(``data/module_test_pages.json``). Environment-specific references are remapped
at import time:

- ``image`` / ``poster_image`` chooser ids → this environment's images
  (distinct local ids map to distinct images so galleries stay varied);
- ``program`` page choosers → the first live program page (same picker as
  ``seed_homepage``);
- the program grid's hand-picked ``items`` → dropped when the ids don't exist
  here (empty chooser = the module's auto mode);
- the episodes router's ``series`` chooser → Policy Prompt (or any live
  series).

Three entries are ``page_type: basic`` (composable-tabs-test, news-router-test,
podcast-all-episodes-test) — BasicPages created under home, covering the
composable tabs + faceted-listing scopes.

Pages are created under the ArticleListPage as Opinion articles, live, with a
backdated ``publishing_date`` (2019) so the fixtures stay out of the auto
queries (bento/carousels/trending pull recent content — test pages must not
pollute the modules being QA'd; the local originals predate the real content
for the same reason).

Requires a built search index (run ``update_index`` first — page saves index
synchronously; see close-out A.4). Dry-run by default; ``--apply`` writes.
Existing slugs are skipped unless ``--update`` (which rewrites title + body).
These pages are QA fixtures — close-out #9 removes them before launch.
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

DATA_FILE = Path(__file__).parent / 'data' / 'module_test_pages.json'

IMAGE_KEYS = {'image', 'poster_image'}
PROGRAM_KEYS = {'program'}
SERIES_KEYS = {'series'}


class Command(BaseCommand):
    help = 'Create the DS module QA test pages (*-test articles) with remapped references.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Write pages (default: dry run).')
        parser.add_argument('--update', action='store_true',
                            help='Rewrite title/body on pages whose slug already exists.')

    # --- reference remapping -------------------------------------------------

    def _image_map(self, body_json):
        """Stable map: each distinct local image id → a distinct image here."""
        from wagtail.images import get_image_model
        local_ids = sorted({v for v in self._walk_ints(body_json, IMAGE_KEYS)})
        pool = list(get_image_model().objects.order_by('id')
                    .values_list('id', flat=True)[:max(len(local_ids), 1)])
        if not pool:
            raise CommandError('No images in this environment — run the media import first.')
        return {lid: pool[i % len(pool)] for i, lid in enumerate(local_ids)}

    @staticmethod
    def _walk_ints(node, keys, found=None):
        if found is None:
            found = []
        if isinstance(node, dict):
            for k, v in node.items():
                if k in keys and isinstance(v, int) and not isinstance(v, bool):
                    found.append(v)
                else:
                    Command._walk_ints(v, keys, found)
        elif isinstance(node, list):
            for item in node:
                Command._walk_ints(item, keys, found)
        return found

    def _remap(self, node, image_map, program_id, series_id, page_ids):
        """Rewrite chooser ids in place; return the (possibly replaced) node."""
        if isinstance(node, dict):
            for k, v in list(node.items()):
                if k in IMAGE_KEYS and isinstance(v, int) and not isinstance(v, bool):
                    node[k] = image_map[v]
                elif k in PROGRAM_KEYS and isinstance(v, int) and not isinstance(v, bool):
                    node[k] = program_id
                elif k in SERIES_KEYS and isinstance(v, int) and not isinstance(v, bool):
                    node[k] = series_id
                elif k == 'items' and isinstance(v, list):
                    # ListBlock of page choosers ({'type':'item','value': <page id>}):
                    # keep only ids that exist here; an emptied list = auto mode.
                    kept = [item for item in v
                            if not (isinstance(item, dict) and isinstance(item.get('value'), int))
                            or item['value'] in page_ids]
                    node[k] = [self._remap(item, image_map, program_id, series_id, page_ids) for item in kept]
                else:
                    node[k] = self._remap(v, image_map, program_id, series_id, page_ids)
        elif isinstance(node, list):
            return [self._remap(item, image_map, program_id, series_id, page_ids) for item in node]
        return node

    # --- main -----------------------------------------------------------------

    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model
        from wagtail.models import Page
        from articles.models import ArticleListPage, ArticlePage, ArticleTypePage
        from core.models import BasicPage
        from multimedia.models import MultimediaSeriesPage
        from research.models import ProjectPage

        apply_ = options['apply']
        data = json.loads(DATA_FILE.read_text())

        # The articles container is unpublished on some environments — that's
        # fine, children can still live under it.
        parent = ArticleListPage.objects.first()
        if parent is None:
            raise CommandError('No ArticleListPage found.')
        opinion = ArticleTypePage.objects.filter(title__iexact='Opinion').first()
        # The page_published notification signal reads page.owner and the
        # revision user unconditionally — a command-created page needs both.
        owner = get_user_model().objects.filter(is_superuser=True).order_by('id').first()
        if owner is None:
            raise CommandError('No superuser to own the pages — create one first.')
        program = ProjectPage.objects.live().public().first()
        program_id = program.id if program else None
        # The episodes-scope router is series-scoped; Policy Prompt preferred
        # (it has seasons, which the Season facet needs), else any live series.
        series = (MultimediaSeriesPage.objects.live().filter(slug='pp').first()
                  or MultimediaSeriesPage.objects.live().first())
        series_id = series.id if series else None
        page_ids = set(Page.objects.live().values_list('id', flat=True))
        # BasicPage test pages (composable tabs / router scopes) live at root.
        home = Page.objects.filter(slug='home').first() or parent.get_parent()

        image_map = self._image_map(data)
        self.stdout.write(f'parent={parent.slug}  images remapped={image_map}  '
                          f'program={program_id}  series={series_id}')

        backdate = timezone.datetime(2019, 1, 1, tzinfo=timezone.get_current_timezone())

        created = updated = skipped = 0
        for slug, spec in data.items():
            body = self._remap(json.loads(json.dumps(spec['body'])), image_map, program_id, series_id, page_ids)
            basic = spec.get('page_type') == 'basic'
            model = BasicPage if basic else ArticlePage
            existing = model.objects.filter(slug=slug).first()
            if existing and not options['update']:
                skipped += 1
                self.stdout.write(f'  skip   {slug} (exists)')
                continue
            if existing:
                updated += 1
                self.stdout.write(f'  update {slug}')
                if apply_:
                    existing.title = spec['title']
                    existing.body = json.dumps(body)
                    if existing.owner_id is None:
                        existing.owner = owner
                    existing.save_revision(user=owner).publish()
                continue
            created += 1
            self.stdout.write(f'  create {slug}')
            if apply_:
                if basic:
                    page = BasicPage(title=spec['title'], slug=slug,
                                     body=json.dumps(body), owner=owner)
                    home.add_child(instance=page)
                else:
                    page = ArticlePage(
                        title=spec['title'],
                        slug=slug,
                        article_type=opinion,
                        publishing_date=backdate,
                        body=json.dumps(body),
                        owner=owner,
                    )
                    parent.add_child(instance=page)
                page.save_revision(user=owner).publish()

        mode = 'APPLIED' if apply_ else 'DRY RUN (use --apply)'
        self.stdout.write(self.style.SUCCESS(
            f'{mode}: {created} created, {updated} updated, {skipped} skipped'))
