import json
from collections import defaultdict
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from people.models import DPHTerm, PersonPage

from .export_dph_cohorts import SCHEMA


DEFAULT_ARTIFACT = Path(__file__).resolve().parents[2] / 'data' / 'dph-cohorts-23111.json'


class Command(BaseCommand):
    help = 'Import a DPH cohort artifact into PersonPage DPH fields (dry-run by default).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--input',
            default=DEFAULT_ARTIFACT,
            help=f'JSON artifact from export_dph_cohorts (default: {DEFAULT_ARTIFACT}).',
        )
        parser.add_argument('--apply', action='store_true', help='Write changes (default: dry-run).')

    def handle(self, *args, **options):
        path = Path(options['input'])
        try:
            artifact = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError(f'Cannot read {path}: {exc}') from exc
        if artifact.get('schema') != SCHEMA:
            raise CommandError(f'Unsupported cohort artifact schema: {artifact.get("schema")!r}')

        memberships = defaultdict(set)
        identities = {}
        statuses = {}
        term_dates = {}
        for cohort in artifact.get('cohorts') or []:
            try:
                name = cohort['name'].strip()
                start = date.fromisoformat(cohort['start_date'])
                status = cohort['status']
                people = cohort['people']
            except (KeyError, TypeError, ValueError) as exc:
                raise CommandError(f'Invalid cohort row: {cohort!r}') from exc
            if not name or status not in PersonPage.DPHStatus.values or not people:
                raise CommandError(f'Invalid cohort row: {cohort!r}')
            if name in term_dates and term_dates[name] != start:
                raise CommandError(f'Cohort {name!r} has conflicting start dates.')
            term_dates[name] = start
            for person in people:
                try:
                    person_id = int(person['id'])
                    slug = person['slug']
                except (KeyError, TypeError, ValueError) as exc:
                    raise CommandError(f'Invalid person row: {person!r}') from exc
                if person_id in identities and identities[person_id] != slug:
                    raise CommandError(f'Person {person_id} has conflicting slugs in the artifact.')
                if person_id in statuses and statuses[person_id] != status:
                    raise CommandError(f'Person {person_id} appears as both current and alumni.')
                identities[person_id] = slug
                statuses[person_id] = status
                memberships[person_id].add(name)

        if not memberships:
            raise CommandError('The artifact has no cohort memberships.')

        people = PersonPage.objects.in_bulk(memberships)
        missing = sorted(set(memberships) - people.keys())
        mismatched = sorted(
            person_id for person_id, person in people.items()
            if person.slug != identities[person_id]
        )
        if missing or mismatched:
            raise CommandError(
                f'Target person validation failed; missing IDs={missing}, slug mismatches={mismatched}'
            )

        existing_terms = DPHTerm.objects.in_bulk(term_dates, field_name='name')
        bad_dates = sorted(
            name for name, term in existing_terms.items()
            if term.start_date != term_dates[name]
        )
        if bad_dates:
            raise CommandError(f'Existing DPH terms have different start dates: {bad_dates}')

        changes = []
        for person_id, person in sorted(people.items()):
            old_terms = set(person.dph_terms.values_list('name', flat=True))
            new_terms = memberships[person_id]
            if person.dph_status != statuses[person_id] or old_terms != new_terms:
                changes.append(person)
                self.stdout.write(
                    f'{person_id} {person.title}: status {person.dph_status or "(blank)"} '
                    f'-> {statuses[person_id]}; terms {sorted(old_terms)} -> {sorted(new_terms)}'
                )

        missing_terms = sorted(set(term_dates) - existing_terms.keys())
        for name in missing_terms:
            self.stdout.write(f'create term: {name} ({term_dates[name]})')

        if not options['apply']:
            self.stdout.write(
                f'Dry run — {len(changes)} people and {len(missing_terms)} terms would change; '
                'nothing written. Re-run with --apply.'
            )
            return

        with transaction.atomic():
            terms = dict(existing_terms)
            for name in missing_terms:
                terms[name] = DPHTerm.objects.create(name=name, start_date=term_dates[name])
            for person in changes:
                person.dph_status = statuses[person.pk]
                person.dph_terms.set([terms[name] for name in memberships[person.pk]])
                person.save()

        self.stdout.write(self.style.SUCCESS(
            f'Applied {len(changes)} person updates and created {len(missing_terms)} terms.'
        ))
