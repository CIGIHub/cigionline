import json
import tempfile
from datetime import date
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from home.models import HomePage

from people.management.commands.export_dph_cohorts import SCHEMA, cohort_rows
from people.models import DPHTerm, PeoplePage, PersonPage


class DPHCohortCommandTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        home = HomePage.objects.get()
        people = home.add_child(instance=PeoplePage(title='People', slug='cohort-people'))
        cls.alex = people.add_child(instance=PersonPage(title='Alex Example', slug='alex-example'))
        cls.sam = people.add_child(instance=PersonPage(title='Sam Example', slug='sam-example'))

    def artifact_path(self):
        artifact = {
            'schema': SCHEMA,
            'source': {'id': 23111, 'title': 'Current Cohort & Alumni'},
            'cohorts': [
                {
                    'name': 'Fall 2026', 'start_date': '2026-09-01', 'status': 'current',
                    'people': [
                        {'id': self.alex.pk, 'title': self.alex.title, 'slug': self.alex.slug,
                         'url_path': self.alex.url_path},
                    ],
                },
                {
                    'name': 'Fall 2025', 'start_date': '2025-09-01', 'status': 'alumni',
                    'people': [
                        {'id': self.sam.pk, 'title': self.sam.title, 'slug': self.sam.slug,
                         'url_path': self.sam.url_path},
                    ],
                },
                {
                    'name': 'Winter 2024', 'start_date': '2024-01-01', 'status': 'alumni',
                    'people': [
                        {'id': self.sam.pk, 'title': self.sam.title, 'slug': self.sam.slug,
                         'url_path': self.sam.url_path},
                    ],
                },
            ],
        }
        handle = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(artifact, handle)
        handle.close()
        self.addCleanup(Path(handle.name).unlink, missing_ok=True)
        return handle.name

    def test_import_is_dry_run_by_default_then_applies_and_is_idempotent(self):
        path = self.artifact_path()
        call_command('import_dph_cohorts', input=path)
        self.alex.refresh_from_db()
        self.assertEqual(self.alex.dph_status, '')
        self.assertFalse(DPHTerm.objects.exists())

        call_command('import_dph_cohorts', input=path, apply=True)
        call_command('import_dph_cohorts', input=path, apply=True)
        self.alex.refresh_from_db()
        self.sam.refresh_from_db()
        self.assertEqual(self.alex.dph_status, PersonPage.DPHStatus.CURRENT)
        self.assertEqual(list(self.alex.dph_terms.values_list('name', flat=True)), ['Fall 2026'])
        self.assertEqual(self.sam.dph_status, PersonPage.DPHStatus.ALUMNI)
        self.assertEqual(
            set(self.sam.dph_terms.values_list('name', flat=True)),
            {'Fall 2025', 'Winter 2024'},
        )

    def test_import_rejects_a_target_slug_mismatch(self):
        path = self.artifact_path()
        artifact = json.loads(Path(path).read_text())
        artifact['cohorts'][0]['people'][0]['slug'] = 'wrong-person'
        Path(path).write_text(json.dumps(artifact))
        with self.assertRaisesMessage(CommandError, 'slug mismatches'):
            call_command('import_dph_cohorts', input=path)

    def test_export_parser_preserves_multi_term_people(self):
        body = [
            {'type': 'persons_list_block', 'value': {
                'title': 'Current', 'cohort': 'Fall 2026',
                'persons': [{'type': 'person', 'value': 10}],
            }},
            {'type': 'persons_list_block', 'value': {
                'title': 'Current', 'cohort': 'Winter 2024',
                'persons': [{'type': 'person', 'value': 10}],
            }},
        ]
        self.assertEqual(
            cohort_rows(body),
            [
                ('Fall 2026', date(2026, 9, 1), 'current', [10]),
                ('Winter 2024', date(2024, 1, 1), 'current', [10]),
            ],
        )
