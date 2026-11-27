import json
import re
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from wagtail.models import Page


SCHEMA = 'cigionline.dph-cohorts.v1'
SEASON_MONTHS = {'Winter': 1, 'Spring': 3, 'Summer': 5, 'Fall': 9}


def term_start_date(name):
    match = re.fullmatch(r'(Winter|Spring|Summer|Fall) (\d{4})', name)
    if not match:
        raise CommandError(f'Unsupported cohort name {name!r}; expected "Season YYYY".')
    season, year = match.groups()
    return date(int(year), SEASON_MONTHS[season], 1)


def cohort_rows(body):
    rows = []
    statuses = {}
    for block in body:
        if block.get('type') != 'persons_list_block':
            continue
        value = block.get('value') or {}
        name = (value.get('cohort') or '').strip()
        title = (value.get('title') or '').strip().lower()
        if not name:
            raise CommandError('A persons-list block has no cohort name.')
        if title not in ('current', 'alumni'):
            raise CommandError(
                f'Cohort {name!r} has unsupported title {value.get("title")!r}; '
                'expected Current or Alumni.'
            )
        status = 'current' if title == 'current' else 'alumni'
        ids = [item.get('value') for item in value.get('persons', [])
               if item.get('type') == 'person']
        if not ids or any(not isinstance(person_id, int) for person_id in ids):
            raise CommandError(f'Cohort {name!r} has a missing or invalid person ID.')
        for person_id in ids:
            if person_id in statuses and statuses[person_id] != status:
                raise CommandError(
                    f'Person {person_id} appears as both current and alumni.'
                )
            statuses[person_id] = status
        rows.append((name, term_start_date(name), status, ids))
    if not rows:
        raise CommandError('No persons_list_block cohorts found on the source page.')
    return rows


class Command(BaseCommand):
    help = 'Export DPH cohort memberships from the legacy Current Cohort & Alumni page.'

    def add_arguments(self, parser):
        parser.add_argument('--page-id', type=int, default=23111)
        parser.add_argument('--output', required=True, help='New JSON artifact path.')

    def handle(self, *args, **options):
        output = Path(options['output'])
        if output.exists():
            raise CommandError(f'Refusing to overwrite existing file: {output}')

        page = Page.objects.filter(pk=options['page_id']).values(
            'id', 'title', 'slug', 'url_path', 'content_type__app_label',
            'content_type__model',
        ).first()
        page_type = (page or {}).get('content_type__app_label'), (page or {}).get(
            'content_type__model'
        )
        if not page or page_type != ('core', 'basicpage'):
            raise CommandError(f'Page {options["page_id"]} is not a core.BasicPage.')

        with connection.cursor() as cursor:
            cursor.execute('SELECT body FROM core_basicpage WHERE page_ptr_id = %s', [page['id']])
            row = cursor.fetchone()
        if not row:
            raise CommandError(f'BasicPage {page["id"]} has no database row.')
        body = row[0] if isinstance(row[0], list) else json.loads(row[0])
        cohorts = cohort_rows(body)

        person_ids = {person_id for _, _, _, ids in cohorts for person_id in ids}
        people = {
            person['id']: person
            for person in Page.objects.filter(pk__in=person_ids).values(
                'id', 'title', 'slug', 'url_path', 'content_type__app_label',
                'content_type__model',
            )
        }
        missing = sorted(person_ids - people.keys())
        wrong_type = sorted(
            person_id for person_id, person in people.items()
            if (person['content_type__app_label'], person['content_type__model'])
            != ('people', 'personpage')
        )
        if missing or wrong_type:
            raise CommandError(
                f'Invalid person references; missing={missing}, not PersonPages={wrong_type}'
            )

        artifact = {
            'schema': SCHEMA,
            'source': {key: page[key] for key in ('id', 'title', 'slug', 'url_path')},
            'cohorts': [
                {
                    'name': name,
                    'start_date': start.isoformat(),
                    'status': status,
                    'people': [
                        {key: people[person_id][key]
                         for key in ('id', 'title', 'slug', 'url_path')}
                        for person_id in ids
                    ],
                }
                for name, start, status, ids in cohorts
            ],
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(artifact, indent=2) + '\n')
        self.stdout.write(
            f'Exported {len(cohorts)} cohorts, {len(person_ids)} people and '
            f'{sum(len(ids) for _, _, _, ids in cohorts)} memberships to {output}'
        )
