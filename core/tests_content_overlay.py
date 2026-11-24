import json
import tempfile
from pathlib import Path
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import SimpleTestCase
from wagtail.test.utils import WagtailPageTestCase

from core.management.commands.export_recent_pages import SCHEMA
from core.management.commands.import_content_overlay import (
    PendingPage,
    remap_references,
    resolve_dependency,
    set_json_reference,
)
from core.models import BasicPage, PrivacyNoticePage
from home.models import HomePage


class ContentOverlayReferenceTests(SimpleTestCase):
    def test_remaps_nested_streamfield_reference_by_block_id(self):
        value = [
            {
                "id": "outer",
                "type": "module",
                "value": {"items": [{"id": "chooser", "type": "item", "value": 12}]},
            }
        ]

        set_json_reference(value, "outer.items.chooser", 34)

        self.assertEqual(value[0]["value"]["items"][0]["value"], 34)

    def test_leaves_many_to_many_reference_for_relation_import(self):
        entry = {
            "stable_key": {"model": "research.projectpage"},
            "references": [{
                "content_path": "project_types",
                "dependency": "research.projecttype:1",
                "model_path": "project_types",
            }],
            "model_rows": {},
            "child_relations": {},
            "_dependencies": {"research.projecttype:1": {"source_pk": "1"}},
        }

        remap_references(
            entry,
            {"research.projecttype:1": SimpleNamespace(pk=2)},
        )


class ContentOverlayPageCreationTests(WagtailPageTestCase):
    def test_prepares_missing_basic_page_dependency(self):
        dependency = {
            "source_pk": "900002",
            "stable_key": {
                "model": "core.basicpage",
                "parent_url_path": "/home/",
                "slug": "linked-landing",
            },
            "rows": {"wagtailcore_page": {
                "title": "Linked landing",
                "url_path": "/home/linked-landing/",
            }},
        }
        pending = {}

        target = resolve_dependency(
            dependency,
            create_missing_pages=True,
            pending_pages=pending,
        )

        self.assertIsInstance(target, PendingPage)
        self.assertEqual(target.entry["source_pk"], "900002")

    def test_moves_conflicting_page_type_and_creates_basic_page(self):
        home = HomePage.objects.get()
        get_user_model().objects.create_user(username="overlay-operator")
        legacy = home.add_child(instance=PrivacyNoticePage(
            title="Legacy landing",
            slug="new-landing",
        ))
        artifact = {
            "schema": SCHEMA,
            "pages": [{
                "source_pk": "900001",
                "stable_key": {
                    "model": "core.basicpage",
                    "parent_url_path": "/home/",
                    "slug": "new-landing",
                },
                "title": "New landing",
                "url_path": "/home/new-landing/",
                "model_rows": {},
                "child_relations": {},
                "many_to_many": {},
                "references": [],
            }],
            "dependencies": {},
        }

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(artifact))
            call_command(
                "import_content_overlay",
                "--artifact", str(path),
                "--model", "core.basicpage",
                "--create-missing-pages",
                "--user", "overlay-operator",
                "--apply",
            )

        legacy.refresh_from_db()
        created = BasicPage.objects.get(slug="new-landing")
        self.assertEqual(legacy.slug, "new-landing-legacy")
        self.assertEqual(created.url_path, "/home/new-landing/")
        self.assertTrue(created.live)
