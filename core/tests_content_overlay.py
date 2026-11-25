import json
import tempfile
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase
from django.utils import timezone
from wagtail.test.utils import WagtailPageTestCase

from core.management.commands.export_recent_pages import SCHEMA
from core.management.commands.import_content_overlay import (
    DEFAULT_MODELS,
    PendingPage,
    is_approved_default_page,
    remap_references,
    resolve_dependency,
    set_json_reference,
    target_title_variants,
)
from core.models import BasicPage, PrivacyNoticePage
from home.models import HomePage
from menus.models import Menu, MenuItem


class ContentOverlayReferenceTests(SimpleTestCase):
    def test_landing_pages_are_approved_but_detail_pages_are_not(self):
        self.assertIn("articles.articlelandingpage", DEFAULT_MODELS)
        self.assertNotIn("articles.articlepage", DEFAULT_MODELS)
        self.assertIn("events.eventlistpage", DEFAULT_MODELS)
        self.assertNotIn("events.eventpage", DEFAULT_MODELS)
        self.assertIn("people.personlistpage", DEFAULT_MODELS)
        self.assertNotIn("people.personpage", DEFAULT_MODELS)

    def test_only_the_experts_person_list_is_approved_by_default(self):
        def entry(page_type):
            return {
                "stable_key": {"model": "people.personlistpage"},
                "model_rows": {
                    "people_personlistpage": {"person_list_page_type": page_type}
                },
            }

        self.assertTrue(is_approved_default_page(entry(1)))
        self.assertFalse(is_approved_default_page(entry(2)))
        self.assertFalse(is_approved_default_page(entry(3)))

    def test_resolves_renamed_page_titles_in_both_directions(self):
        self.assertIn(
            "Freedom of Thought",
            target_title_variants(
                "research.projectpage", "Legitimate Influence or Unlawful Manipulation?"
            ),
        )
        self.assertIn(
            "Global Economic Scenarios",
            target_title_variants(
                "research.projectpage", "Multilateral and Institutional Reform"
            ),
        )
        self.assertIn(
            "Leadership",
            target_title_variants(
                "people.personlistpage", "Leadership, Partners and Team"
            ),
        )

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


class ContentOverlayMenuTests(WagtailPageTestCase):
    def test_rejects_requested_page_missing_from_artifact(self):
        artifact = {"schema": SCHEMA, "pages": [], "dependencies": {}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(artifact))
            with self.assertRaisesMessage(CommandError, "absent from the artifact"):
                call_command(
                    "import_content_overlay",
                    "--artifact", str(path),
                    "--page-url-path", "/home/missing/",
                )

    def test_exports_menu_page_links_as_stable_dependencies(self):
        home = HomePage.objects.get()
        menu = Menu.objects.create(name="Overlay export", slug="overlay-export")
        MenuItem.objects.create(menu=menu, title="Home", link_page=home, sort_order=0)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            call_command(
                "export_recent_pages",
                "--output", str(path),
                "--since", (timezone.now() + timedelta(days=1)).isoformat(),
                "--include-url-path", home.url_path,
            )
            artifact = json.loads(path.read_text())

        exported = next(entry for entry in artifact["menus"] if entry["slug"] == menu.slug)
        dependency = artifact["dependencies"][exported["items"][0]["link_page"]]
        self.assertEqual(dependency["stable_key"]["model"], "home.homepage")
        self.assertEqual(dependency["rows"]["wagtailcore_page"]["url_path"], home.url_path)
        self.assertEqual(artifact["counts"]["pages"], 1)

    def test_replaces_menus_by_slug_and_remaps_page_links(self):
        home = HomePage.objects.get()
        get_user_model().objects.create_user(username="overlay-operator")
        Menu.objects.filter(
            slug__in=["primary-nav", "nav-topics-standard", "target-only"]
        ).delete()
        Menu.objects.filter(slug="", name="Media").delete()
        primary = Menu.objects.create(name="Old primary", slug="primary-nav")
        MenuItem.objects.create(menu=primary, title="Old item")
        target_only = Menu.objects.create(name="Keep me", slug="target-only")
        media = Menu.objects.create(name="Media", slug="")
        MenuItem.objects.create(menu=media, title="Old media item")
        dependency_id = f"home.homepage:{home.pk}"
        artifact = {
            "schema": SCHEMA,
            "pages": [],
            "menus": [
                {
                    "name": "Primary navigation",
                    "slug": "primary-nav",
                    "bottom_link_label": "Home",
                    "bottom_link_url": "",
                    "bottom_link_page": dependency_id,
                    "items": [{
                        "title": "Research",
                        "description": "",
                        "link_url": "",
                        "link_page": dependency_id,
                        "submenu": "nav-topics-standard",
                        "sort_order": 0,
                    }],
                },
                {
                    "name": "Topics",
                    "slug": "nav-topics-standard",
                    "bottom_link_label": "",
                    "bottom_link_url": "",
                    "bottom_link_page": None,
                    "items": [{
                        "title": "Theme",
                        "description": "Theme description",
                        "link_url": "/themes/theme/",
                        "link_page": None,
                        "submenu": None,
                        "sort_order": 0,
                    }],
                },
                {
                    "name": "Media",
                    "slug": "",
                    "bottom_link_label": "",
                    "bottom_link_url": "",
                    "bottom_link_page": None,
                    "items": [{
                        "title": "Media Relations",
                        "description": "",
                        "link_url": "/media-relations/",
                        "link_page": None,
                        "submenu": None,
                        "sort_order": 0,
                    }],
                },
            ],
            "dependencies": {
                dependency_id: {
                    "source_pk": str(home.pk),
                    "stable_key": {
                        "model": "home.homepage",
                        "parent_url_path": "/",
                        "slug": "home",
                    },
                    "rows": {"wagtailcore_page": {
                        "title": home.title,
                        "url_path": home.url_path,
                    }},
                },
            },
        }

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(artifact))
            for _ in range(2):
                call_command(
                    "import_content_overlay",
                    "--artifact", str(path),
                    "--import-menus",
                    "--user", "overlay-operator",
                    "--apply",
                )

        primary.refresh_from_db()
        item = primary.menu_items.get()
        self.assertEqual(primary.name, "Primary navigation")
        self.assertEqual(primary.bottom_link_page_id, home.pk)
        self.assertEqual(item.title, "Research")
        self.assertEqual(item.link_page_id, home.pk)
        self.assertEqual(item.submenu.slug, "nav-topics-standard")
        self.assertEqual(Menu.objects.filter(slug="nav-topics-standard").count(), 1)
        media.refresh_from_db()
        self.assertEqual(media.menu_items.get().title, "Media Relations")
        self.assertTrue(Menu.objects.filter(pk=target_only.pk).exists())
