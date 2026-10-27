import importlib
import shutil
import tempfile

from core.heroes import publication_hero_data
from django.apps import apps
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.test import TestCase, override_settings
from django.utils import timezone
from home.models import HomePage, Think7HomePage
from modelcluster.models import model_from_serializable_data
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Revision
from wagtail.test.utils import WagtailPageTestCase

from .models import (
    PublicationListPage,
    PublicationPage,
    PublicationSeriesListPage,
    PublicationSeriesPage,
    PublicationTypePage,
    T7PublicationPage,
)

from articles.models import ArticlePage, ArticleSeriesListPage, ArticleTypePage


class PublicationListPageTests(WagtailPageTestCase):
    def test_publicationlistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            PublicationListPage,
            {HomePage, Think7HomePage},
        )

    def test_publicationlistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            PublicationListPage,
            {PublicationPage, PublicationTypePage, PublicationSeriesListPage, ArticleSeriesListPage, ArticleTypePage, T7PublicationPage},
        )


class PublicationPageTests(WagtailPageTestCase):
    def test_publicationpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            PublicationPage,
            {PublicationListPage},
        )

    def test_publicationpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            PublicationPage,
            {},
        )


class PublicationSeriesListPageTests(WagtailPageTestCase):
    def test_publicationserieslistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            PublicationSeriesListPage,
            {HomePage, PublicationListPage},
        )

    def test_publicationserieslistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            PublicationSeriesListPage,
            {PublicationSeriesPage},
        )


class PublicationSeriesPageTests(WagtailPageTestCase):
    def test_publicationseriespage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            PublicationSeriesPage,
            {PublicationSeriesListPage},
        )

    def test_publicationseriespage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            PublicationSeriesPage,
            {},
        )


class PublicationTypePageTests(WagtailPageTestCase):
    def test_publicationtypepage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            PublicationTypePage,
            {PublicationListPage},
        )

    def test_publicationtypepage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            PublicationTypePage,
            {},
        )


class PublicationHeroBannerDefaultTests(TestCase):
    """The publication hero banner is opt-in (Tim, BugHerd #520): new and
    revision-loaded publications default off, other content types keep the
    shared default on, and 0074 switches existing publications off in the table
    and in their revisions. Builds its own pages — no people.json fixture."""

    @classmethod
    def setUpTestData(cls):
        cls.home = HomePage.objects.get()
        # Publishing fires the notification signal, which reads the owner's name.
        cls.owner = get_user_model().objects.create_user(
            username='editor', email='editor@example.com', first_name='Ed', last_name='Itor')
        cls.publication_type = cls.home.add_child(instance=PublicationTypePage(title='Policy Briefs', slug='policy-briefs'))
        cls.article_type = cls.home.add_child(instance=ArticleTypePage(title='Opinion', slug='opinion'))

    def publication(self, slug, **kwargs):
        return self.home.add_child(instance=PublicationPage(
            title=slug, slug=slug, publishing_date=timezone.now(), owner=self.owner,
            publication_type=self.publication_type, **kwargs))

    def revision_content(self, page):
        return Revision.objects.get(pk=page.latest_revision_id).content

    def test_new_publication_defaults_banner_off(self):
        self.assertFalse(PublicationPage().show_hero_banner)
        self.assertFalse(self.publication('new-pub').show_hero_banner)

    def test_revision_without_key_loads_banner_off(self):
        # The editor rebuilds the page from revision JSON; pre-field revisions
        # carry no key and must load the new default.
        page = model_from_serializable_data(PublicationPage, {'pk': None, 'title': 'x'}, check_fks=False)
        self.assertFalse(page.show_hero_banner)

    def test_article_keeps_banner_on_by_default(self):
        self.assertTrue(ArticlePage().show_hero_banner)

    def test_migration_turns_banner_off_in_table_and_revisions(self):
        # Explicit true in the table and in every revision: an older one, the
        # live one and a draft on top.
        explicit = self.publication('explicit-true', show_hero_banner=True)
        historical = explicit.save_revision(user=self.owner)
        live = explicit.save_revision(user=self.owner)
        live.publish()
        explicit.title = 'explicit-true draft'
        explicit.save_revision(user=self.owner)
        # Table true, revision saved before the field existed (no key).
        keyless = self.publication('keyless', show_hero_banner=True)
        keyless_revision = keyless.save_revision(user=self.owner)
        keyless_revision.publish()
        del keyless_revision.content['show_hero_banner']
        keyless_revision.save(update_fields=['content'])
        # Another page type sharing the field.
        article = self.home.add_child(instance=ArticlePage(
            title='article', slug='article', publishing_date=timezone.now(), owner=self.owner,
            article_type=self.article_type, show_hero_banner=True))
        article.save_revision(user=self.owner).publish()
        revision_count = Revision.objects.count()
        explicit.refresh_from_db()
        latest_created_at = explicit.latest_revision_created_at

        migration = importlib.import_module('publications.migrations.0074_publicationpage_hero_banner_off')
        migration.hero_banner_off(apps, None)
        migration.hero_banner_off(apps, None)  # idempotent

        explicit.refresh_from_db()
        keyless.refresh_from_db()
        article.refresh_from_db()
        self.assertFalse(explicit.show_hero_banner)
        self.assertFalse(keyless.show_hero_banner)
        self.assertEqual(explicit.live_revision_id, live.pk)
        self.assertNotEqual(explicit.latest_revision_id, live.pk)
        self.assertEqual(explicit.latest_revision_created_at, latest_created_at)
        for pk in (historical.pk, live.pk, explicit.latest_revision_id):
            self.assertIs(Revision.objects.get(pk=pk).content['show_hero_banner'], False)
        self.assertNotIn('show_hero_banner', self.revision_content(keyless))
        self.assertEqual(self.revision_content(explicit)['title'], 'explicit-true draft')
        self.assertTrue(article.show_hero_banner)
        self.assertIs(self.revision_content(article)['show_hero_banner'], True)
        self.assertEqual(Revision.objects.count(), revision_count)


class PublicationHeroBannerRenderTests(TestCase):
    """With the toggle off, a hero-sized feature image no longer renders as a
    banner (Tim, BugHerd #520); turning it on still does."""

    @classmethod
    def setUpClass(cls):
        cls.media_root = tempfile.mkdtemp()
        cls.media = override_settings(MEDIA_ROOT=cls.media_root)
        cls.media.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.media.disable()
        shutil.rmtree(cls.media_root, ignore_errors=True)

    @classmethod
    def setUpTestData(cls):
        image = get_image_model().objects.create(
            title='Feature', file=get_test_image_file('feature.png', size=(1600, 686)))
        home = HomePage.objects.get()
        cls.page = home.add_child(instance=PublicationPage(
            title='Policy Brief', slug='policy-brief', publishing_date=timezone.now(), image_feature=image,
            publication_type=home.add_child(instance=PublicationTypePage(title='Policy Briefs', slug='policy-briefs'))))

    def render_hero(self):
        hero = publication_hero_data(self.page)
        return hero, render_to_string('includes/heroes/content_hero.html', {'hero': hero, 'page': self.page})

    def test_no_banner_by_default(self):
        hero, html = self.render_hero()
        self.assertGreaterEqual(hero['image'].width, 1280)
        self.assertFalse(hero['banner'])
        self.assertNotIn('ds-hero__banner', html)

    def test_banner_when_turned_on(self):
        self.page.show_hero_banner = True
        hero, html = self.render_hero()
        self.assertTrue(hero['banner'])
        self.assertIn('ds-hero__banner', html)
