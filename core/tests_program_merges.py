from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from django.utils import timezone

from events.models import EventListPage, EventPage
from home.models import HomePage
from people.models import PeoplePage, PersonPage, PersonType
from publications.models import PublicationListPage, PublicationPage, PublicationTypePage
from research.models import ProjectPage, ThemePage, ThemeProgram
from streams.blocks import (
    ExpertsCarouselBlock,
    FacetedListingBlock,
    GESEventsBlock,
    ProgramGridBlock,
    ProgramSpotlightBlock,
    program_module_context,
    scope_content_qs,
)

from .faceted_listing import build_listing_context
from .models import ContentPage
from search.search import expand_program_filters


class MergedProgramScopeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.home = HomePage.objects.get()
        cls.theme = cls.home.add_child(instance=ThemePage(
            title='Theme', slug='merged-program-theme'))
        cls.primary = cls.home.add_child(instance=ProjectPage(
            title='Primary Program', slug='primary-program', publishing_date=timezone.now()))
        cls.legacy = cls.home.add_child(instance=ProjectPage(
            title='Legacy Program', slug='legacy-program', publishing_date=timezone.now()))
        cls.other = cls.home.add_child(instance=ProjectPage(
            title='Other Program', slug='other-program', publishing_date=timezone.now()))
        ThemeProgram.objects.create(theme=cls.theme, program=cls.primary)
        cls.primary.merged_programs.set([cls.legacy])
        cls.primary.save()

        cls.publications = cls.home.add_child(instance=PublicationListPage(
            title='Publications', slug='merged-program-publications'))
        cls.publication_type = cls.home.add_child(instance=PublicationTypePage(
            title='Policy Briefs', slug='merged-program-policy-briefs'))
        cls.primary_content = cls.make_publication('Primary Content', cls.primary)
        cls.legacy_content = cls.make_publication('Legacy Content', cls.legacy)
        cls.other_content = cls.make_publication('Other Content', cls.other)

        events = cls.home.add_child(instance=EventListPage(
            title='Events', slug='merged-program-events'))
        cls.legacy_event = events.add_child(instance=EventPage(
            title='Legacy Event', slug='legacy-event',
            publishing_date=timezone.now() + timedelta(days=1)))
        cls.legacy_event.projects.set([cls.legacy])
        cls.legacy_event.save()

        people = cls.home.add_child(instance=PeoplePage(
            title='People', slug='merged-program-people'))
        cls.legacy_expert = people.add_child(instance=PersonPage(
            title='Legacy Expert', slug='legacy-expert', last_name='Expert'))
        cls.legacy_expert.person_types.set([PersonType.objects.get(name='Expert')])
        cls.legacy_expert.projects.set([cls.legacy])
        cls.legacy_expert.save()

    @classmethod
    def make_publication(cls, title, program):
        page = cls.publications.add_child(instance=PublicationPage(
            title=title,
            slug=title.lower().replace(' ', '-'),
            publishing_date=timezone.now(),
            publication_type=cls.publication_type,
        ))
        page.projects.set([program])
        page.save()
        return page

    def titles(self, pages):
        return {page.title for page in pages}

    def test_shared_scope_includes_primary_and_legacy_content(self):
        pages = scope_content_qs(ContentPage.objects.live(), self.primary).specific()
        self.assertEqual(
            self.titles(pages), {'Primary Content', 'Legacy Content', 'Legacy Event'})
        self.assertTrue(self.primary.has_tagged_pages)

    def test_theme_dynamic_scope_expands_its_primary_programs(self):
        pages = scope_content_qs(ContentPage.objects.live(), self.theme).specific()
        self.assertEqual(
            self.titles(pages), {'Primary Content', 'Legacy Content', 'Legacy Event'})

    def test_program_module_includes_legacy_content(self):
        value = ProgramGridBlock().to_python({'program_source': 'auto', 'count': 10})
        context = program_module_context(value, self.primary)
        self.assertEqual(
            self.titles(context['pages']), {'Primary Content', 'Legacy Content', 'Legacy Event'})

    def test_program_spotlight_includes_legacy_content(self):
        entry = ProgramSpotlightBlock._spotlight_entry(
            self.primary, self.theme, self.primary.title)
        self.assertIn('Legacy Event', self.titles(entry['content_pages']))

    def test_legacy_program_event_block_uses_expanded_scope(self):
        block = GESEventsBlock()
        value = block.to_python({'title': 'Events', 'project': self.primary.pk})
        context = block.get_context(value)
        self.assertEqual(list(context['events']), [self.legacy_event])

    def test_search_program_filter_expands_to_legacy_programs(self):
        self.assertEqual(
            expand_program_filters([str(self.primary.pk), 'invalid']),
            [self.primary.pk, self.legacy.pk, 'invalid'],
        )

    def test_faceted_listing_includes_legacy_content(self):
        block = FacetedListingBlock()
        value = block.to_python({
            'card_type': 'resource',
            'program_source': 'auto',
            'content_types': ['publication'],
            'prefix': 'merged',
        })
        context = build_listing_context(
            RequestFactory().get('/'), value, page=self.primary)
        self.assertEqual(
            self.titles(context['router_results']),
            {'Primary Content', 'Legacy Content'},
        )

    def test_archive_does_not_repeat_content_from_included_programs(self):
        block = FacetedListingBlock()
        value = block.to_python({
            'card_type': 'resource',
            'program_source': 'none',
            'content_types': ['publication'],
            'prefix': 'archive',
        })
        context = build_listing_context(RequestFactory().get('/'), value)
        self.assertEqual(self.titles(context['router_results']), {'Other Content'})

    def test_program_experts_include_legacy_program_relationships(self):
        block = ExpertsCarouselBlock()
        value = block.to_python({'mode': 'program', 'count': 12})
        experts = block.get_context(value, {'page': self.primary})['experts']
        self.assertEqual(experts, [self.legacy_expert])

    def test_existing_content_relationship_is_not_rewritten(self):
        self.assertEqual(list(self.legacy_content.projects.all()), [self.legacy])

    def test_included_program_cannot_have_two_primaries(self):
        other_primary = self.home.add_child(instance=ProjectPage(
            title='Another Primary', slug='another-primary', publishing_date=timezone.now()))
        with self.assertRaisesMessage(
                ValidationError, 'An included program can belong to only one primary program.'):
            other_primary.validate_merged_programs(
                ProjectPage.objects.filter(pk=self.legacy.pk))

    def test_merge_chains_are_rejected(self):
        with self.assertRaisesMessage(
                ValidationError, 'An included program cannot itself include other programs.'):
            self.other.validate_merged_programs(
                ProjectPage.objects.filter(pk=self.primary.pk))
