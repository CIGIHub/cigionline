import uuid
from datetime import date
from types import SimpleNamespace

from annual_reports.models import AnnualReportListPage
from careers.models import JobPostingListPage
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone
from home.models import HomePage, Think7HomePage
from people.models import DPHTerm, PeoplePage, PersonListPage, PersonPage, PersonType
from publications.models import PublicationPage, PublicationTypePage
from research.models import (
    ProjectPage,
    ThemePage,
    ThemeProgram,
    TopicPage,
)
from streams.blocks import FacetedListingBlock, VideoTextBlock
from wagtail.admin.panels import MultiFieldPanel
from wagtail.blocks import StructValue
from wagtail.test.utils import WagtailPageTestCase

from .faceted_listing import build_listing_context, default_listing_prefix
from .heroes import _topic_eyebrow, hero_data, person_hero_data
from .models import (
    BasicPage,
    FundingPage,
    PrivacyNoticePage,
    TwentiethPage,
    TwentiethPageSingleton,
)


class BasicPageTests(WagtailPageTestCase):
    def test_basicpage_parent_page_types(self):
        """
        Verify allowed parent page types.
        """
        self.assertAllowedParentPageTypes(
            BasicPage,
            {BasicPage, HomePage, JobPostingListPage, Think7HomePage}
        )

    def test_basicpage_child_page_types(self):
        """
        Verify allowed child page types.
        """
        self.assertAllowedSubpageTypes(
            BasicPage,
            {AnnualReportListPage, BasicPage, FundingPage, PersonListPage, ProjectPage, TwentiethPage, TwentiethPageSingleton}
        )


class FundingPageTests(WagtailPageTestCase):
    def test_fundingpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            FundingPage,
            {BasicPage},
        )

    def test_fundingpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            FundingPage,
            {},
        )


class PrivacyNoticePageTests(WagtailPageTestCase):
    def test_privacynoticepage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            PrivacyNoticePage,
            {HomePage},
        )

    def test_privacynoticepage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            PrivacyNoticePage,
            {},
        )


class VideoTextBlockRenderTests(SimpleTestCase):
    """No video set → a plain poster image with no play affordance; any video
    keeps the facade markup (BugHerd #535)."""

    FACADE_MARKERS = ('data-ds-video', 'ds-video__overlay', 'ds-video__play', 'Play video')

    def render(self, video_file=None, video_url=''):
        block = VideoTextBlock()
        value = block.to_python({'heading': 'Heading', 'intro_text': '<p>Intro</p>', 'buttons': []})
        values = dict(value, poster_image=None, video_file=video_file, video_url=video_url)
        return block.render(StructValue(block, list(values.items())), context={'page': None})

    def test_no_video_renders_static_image_without_play_affordance(self):
        html = self.render()
        self.assertIn('class="ds-video ds-video--static"', html)
        for marker in self.FACADE_MARKERS:
            self.assertNotIn(marker, html)

    def test_video_url_keeps_facade(self):
        html = self.render(video_url='https://youtu.be/abc123')
        self.assertIn('data-ds-video-url="https://youtu.be/abc123"', html)
        self.assertNotIn('data-ds-video-file', html)
        for marker in self.FACADE_MARKERS:
            self.assertIn(marker, html)
        self.assertNotIn('ds-video--static', html)

    def test_video_file_keeps_facade(self):
        video_file = SimpleNamespace(file=SimpleNamespace(url='/media/clip.mp4'))
        html = self.render(video_file=video_file)
        self.assertIn('data-ds-video-file="/media/clip.mp4"', html)
        self.assertNotIn('data-ds-video-url', html)
        for marker in self.FACADE_MARKERS:
            self.assertIn(marker, html)
        self.assertNotIn('ds-video--static', html)


class PersonRoleCrumbTests(TestCase):
    """A person's trail names their role listing (BugHerd #361/#516). Board
    members and senior management land on the Leadership page's Senior
    Management and Board of Directors tab, not Experts (BugHerd #527). Builds
    its own pages — no people.json fixture."""

    @staticmethod
    def listing(card_type, person_type=None):
        # The full value an editor's save stores (every field, prefix blank as
        # on staging), so the default prefix is the one the listing renders.
        block = FacetedListingBlock()
        value = {'card_type': card_type, 'prefix': ''}
        if person_type:
            value['person_type'] = person_type
        return block.get_prep_value(block.to_python(value))

    @classmethod
    def setUpTestData(cls):
        cls.board_listing = cls.listing('person', 'management_board')
        cls.staff_listing = cls.listing('staff')
        cls.expert_listing = cls.listing('expert')
        cls.home = HomePage.objects.get()
        cls.people = cls.home.add_child(instance=PeoplePage(title='People', slug='people'))
        cls.experts = cls.home.add_child(instance=PersonListPage(
            title='Experts', slug='experts',
            body=[{'type': 'faceted_listing', 'value': cls.expert_listing}]))

    @staticmethod
    def tab(label, listing):
        # A ListBlock item as stored (type/value/id).
        return {'type': 'item', 'id': str(uuid.uuid4()), 'value': {
            'label': label, 'content': [{'type': 'faceted_listing', 'value': listing}]}}

    def make_leadership(self, *tabs):
        # Staging's page 23820 shape: one composable_tabs block, blank prefixes.
        return self.home.add_child(instance=BasicPage(
            title='Leadership, Partners and Team', slug='leadership-partners-and-team',
            body=[{'type': 'composable_tabs', 'value': {'heading': '', 'tabs': list(tabs)}}]))

    def make_full_leadership(self):
        return self.make_leadership(
            self.tab('Senior Management and Board of Directors', self.board_listing),
            self.tab('Staff Directory', self.staff_listing))

    def make_person(self, slug, types):
        person = self.people.add_child(instance=PersonPage(title=slug, slug=slug))
        person.person_types.set([PersonType.objects.get(name=name) for name in types])
        person.save()
        return PersonPage.objects.get(pk=person.pk)

    def crumbs(self, person):
        return person_hero_data(person)['breadcrumb']

    def leadership_tab_url(self, leadership, slug, listing):
        prefix = default_listing_prefix(listing)
        return '%s?tab=%s#router-%s' % (leadership.url, slug, prefix)

    def assertTrail(self, person, title, url):
        self.assertEqual(self.crumbs(person), [
            {'title': 'Home', 'url': '/'}, {'title': title, 'url': url}])

    def test_board_member_trails_to_board_of_directors(self):
        # anil-arora's case: Board Member is his only type.
        leadership = self.make_full_leadership()
        url = self.leadership_tab_url(
            leadership, 'senior-management-and-board-of-directors', self.board_listing)
        self.assertTrail(self.make_person('board', ['Board Member']), 'Board of Directors', url)
        # The tab and anchor are the ones the Leadership page actually renders.
        response = self.client.get(url.split('#')[0])
        self.assertContains(response, 'data-tab-slug="senior-management-and-board-of-directors"')
        self.assertContains(response, 'id="router-%s"' % url.split('#router-')[1])

    def test_management_team_trails_to_senior_management(self):
        leadership = self.make_full_leadership()
        url = self.leadership_tab_url(
            leadership, 'senior-management-and-board-of-directors', self.board_listing)
        self.assertNotIn('-type=', url)
        self.assertTrail(
            self.make_person('manager', ['Management Team', 'Staff']), 'Senior Management', url)

    def test_senior_management_outranks_expert_role(self):
        # aaron-shull's case: Management Team + Research Director.
        leadership = self.make_full_leadership()
        self.assertTrail(
            self.make_person('director', ['Management Team', 'Research Director', 'Expert']),
            'Senior Management',
            self.leadership_tab_url(
                leadership, 'senior-management-and-board-of-directors', self.board_listing))

    def test_staff_keeps_staff_directory(self):
        leadership = self.make_full_leadership()
        self.assertTrail(
            self.make_person('staffer', ['Staff']), 'Staff',
            self.leadership_tab_url(leadership, 'staff-directory', self.staff_listing))

    def test_expert_role_keeps_filtered_experts_listing(self):
        self.make_full_leadership()
        prefix = default_listing_prefix(self.expert_listing)
        self.assertTrail(
            self.make_person('fellow', ['Expert', 'Senior Fellow']), 'Senior Fellows',
            '/experts/?%s-type=%s#router-%s' % (
                prefix, PersonType.objects.get(name='Senior Fellow').pk, prefix))

    def test_untyped_falls_back_to_experts(self):
        self.make_full_leadership()
        self.assertTrail(self.make_person('external', []), 'Experts', '/experts/')

    def test_no_leadership_page_falls_through(self):
        # No page to link: the later steps decide, as for Staff under #361.
        self.assertTrail(self.make_person('board', ['Board Member']), 'Experts', '/experts/')
        prefix = default_listing_prefix(self.expert_listing)
        self.assertTrail(
            self.make_person('director', ['Management Team', 'Research Director']),
            'Research Directors', '/experts/?%s-type=19#router-%s' % (prefix, prefix))

    def test_no_board_tab_links_the_leadership_page(self):
        # The page is there but no listing is scoped to management_board: the
        # bare Leadership page, never another tab (_tab_listing_url's contract).
        leadership = self.make_leadership(self.tab('Staff Directory', self.staff_listing))
        self.assertTrail(
            self.make_person('board', ['Board Member']), 'Board of Directors', leadership.url)
        self.assertTrail(
            self.make_person('manager', ['Management Team', 'Staff']), 'Senior Management',
            leadership.url)


class DPHCohortListingTests(TestCase):
    """The DPH "Current Cohort and Alumni" listing filters by Type (Current
    Cohort / Alumni) and Term, from each fellow's DPH Status and DPH Term(s);
    the theme facet reads Topic again (BugHerd #365/#440). Until CIGI fills
    the fields the listing is unchanged. Builds its own pages — no
    people.json fixture."""

    # Staging's block on the DPH hub (page 21321): blank person type and prefix.
    STAGING_LISTING = {
        'card_type': 'person', 'person_type': '', 'facets': ['topic', 'type'],
        'heading': 'Current Cohort and Alumni', 'prefix': ''}

    @staticmethod
    def listing(**value):
        block = FacetedListingBlock()
        return block.get_prep_value(block.to_python(value))

    @classmethod
    def setUpTestData(cls):
        cls.home = HomePage.objects.get()
        cls.people = cls.home.add_child(instance=PeoplePage(title='People', slug='people'))
        cls.ai = cls.home.add_child(instance=ThemePage(
            title='AI and Transformative Technology', slug='ai', accent='security'))
        cls.data = cls.home.add_child(instance=ThemePage(
            title='Data, Economy and Society', slug='data', accent='security'))
        cls.ai_topic = cls.home.add_child(instance=TopicPage(
            title='AI', slug='ai-topic', program_theme=cls.ai))
        cls.data_topic = cls.home.add_child(instance=TopicPage(
            title='Data', slug='data-topic', program_theme=cls.data))
        cls.w24 = DPHTerm.objects.create(name='Winter 2024', start_date=date(2024, 1, 1))
        cls.f24 = DPHTerm.objects.create(name='Fall 2024', start_date=date(2024, 9, 1))
        cls.f25 = DPHTerm.objects.create(name='Fall 2025', start_date=date(2025, 9, 1))
        cls.s26 = DPHTerm.objects.create(name='Summer 2026', start_date=date(2026, 5, 1))
        cls.value = cls.listing(**cls.STAGING_LISTING)
        cls.prefix = default_listing_prefix(cls.value)
        # Twelve fellows with no status or term — the state on handover.
        cls.fellows = [
            cls.make_person('fellow-%02d' % i, ['Digital Policy Hub Fellow'],
                            topic=cls.ai_topic if i % 2 else cls.data_topic)
            for i in range(12)]

    @classmethod
    def make_person(cls, slug, types, topic=None, last_name=''):
        person = cls.people.add_child(instance=PersonPage(
            title=slug, slug=slug, last_name=last_name))
        person.person_types.set([PersonType.objects.get(name=name) for name in types])
        person.save()
        if topic:
            person.derived_topics.set([topic])
        return PersonPage.objects.get(pk=person.pk)

    @staticmethod
    def set_dph(people, status='', terms=()):
        for person in people:
            person.dph_status = status
            person.dph_terms.set(terms)
            person.save()

    def ctx(self, value=None, **params):
        value = value or self.value
        prefix = default_listing_prefix(value)
        request = RequestFactory().get(
            '/', {'%s-%s' % (prefix, k): v for k, v in params.items()})
        return build_listing_context(request, value)

    @staticmethod
    def facet(context, key):
        return next((f for f in context['router_facets'] if f['key'] == key), None)

    @staticmethod
    def slugs(context):
        return sorted(p.slug for p in context['router_results'])

    def statuses(self):
        # Four current (one blank between), four alumni, four blank.
        current, alumni = self.fellows[:4], self.fellows[4:8]
        self.set_dph(current, PersonPage.DPHStatus.CURRENT)
        self.set_dph(alumni, PersonPage.DPHStatus.ALUMNI)
        return current, alumni

    def test_person_page_dph_fields_default_blank(self):
        person = self.fellows[0]
        self.assertEqual(person.dph_status, '')
        self.assertEqual(person.dph_terms.count(), 0)
        self.assertEqual(str(self.f25), 'Fall 2025')
        self.assertEqual(list(DPHTerm.objects.all()),
                         [self.s26, self.f25, self.f24, self.w24])

    def test_no_data_shows_every_fellow_and_only_topic(self):
        context = self.ctx()
        self.assertEqual(context['router_total'], 12)
        self.assertEqual([f['key'] for f in context['router_facets']], ['topic'])
        self.assertEqual(self.facet(context, 'topic')['label'], 'Topic')

    def test_one_status_value_hides_type(self):
        self.set_dph(self.fellows[:5], PersonPage.DPHStatus.CURRENT)
        context = self.ctx()
        self.assertIsNone(self.facet(context, 'type'))
        self.assertEqual(context['router_total'], 12)

    def test_type_facet_offers_all_current_alumni(self):
        self.statuses()
        context = self.ctx()
        self.assertEqual([f['key'] for f in context['router_facets']], ['type', 'topic'])
        facet = self.facet(context, 'type')
        self.assertEqual(facet['label'], 'Type')
        self.assertTrue(facet['single'])
        self.assertEqual([o['label'] for o in facet['options']],
                         ['All', 'Current Cohort', 'Alumni'])
        self.assertEqual([o['checked'] for o in facet['options']], [True, False, False])
        self.assertEqual(context['router_total'], 12)

    def test_filter_by_type(self):
        current, _ = self.statuses()
        context = self.ctx(type='current')
        self.assertEqual(self.slugs(context), sorted(p.slug for p in current))
        self.assertTrue(context['router_has_filters'])
        self.assertEqual([o['checked'] for o in self.facet(context, 'type')['options']],
                         [False, True, False])

    def test_type_ignores_unknown_values(self):
        self.statuses()
        external = PersonType.objects.get(name='External profile')
        for person in self.fellows[:3]:
            person.person_types.add(external)
            person.save()
        # A numeric Role id (the key's old meaning) or junk filters nothing.
        for value in (external.pk, 'bogus'):
            context = self.ctx(type=value)
            self.assertEqual(context['router_total'], 12)
            self.assertFalse(context['router_has_filters'])

    def test_term_facet_lists_only_terms_in_use_newest_first(self):
        self.set_dph(self.fellows[:3], terms=[self.w24])
        self.set_dph(self.fellows[3:6], terms=[self.f24])
        self.set_dph(self.fellows[6:9], terms=[self.f25])
        context = self.ctx()
        facet = self.facet(context, 'term')
        self.assertEqual(facet['label'], 'Term')
        self.assertFalse(facet['open'])
        self.assertEqual([o['label'] for o in facet['options']],
                         ['Fall 2025', 'Fall 2024', 'Winter 2024'])  # no Summer 2026
        self.assertEqual(context['router_facets'][-1]['key'], 'term')
        self.assertEqual(context['router_total'], 12)

    def test_term_facet_hidden_with_one_term(self):
        self.set_dph(self.fellows[:6], terms=[self.f25])
        self.assertIsNone(self.facet(self.ctx(), 'term'))

    def test_filter_by_term_includes_multi_term_fellow(self):
        returning = self.fellows[0]
        self.set_dph([returning], terms=[self.w24, self.f25])
        self.set_dph(self.fellows[1:4], terms=[self.w24])
        self.set_dph(self.fellows[4:6], terms=[self.f25])
        w24 = self.ctx(term=self.w24.pk)
        f25 = self.ctx(term=self.f25.pk)
        self.assertEqual(self.slugs(w24), sorted(p.slug for p in self.fellows[:4]))
        self.assertEqual(self.slugs(f25), sorted(
            p.slug for p in [returning] + self.fellows[4:6]))
        self.assertTrue(w24['router_has_filters'])
        # Both terms (OR within the facet): the returning fellow appears once.
        both = self.ctx(term=[self.w24.pk, self.f25.pk])
        self.assertEqual(both['router_total'], 6)
        self.assertEqual(len(set(self.slugs(both))), 6)
        self.assertEqual([o['checked'] for o in self.facet(w24, 'term')['options']],
                         [False, True])

    def test_type_and_term_combine(self):
        self.set_dph(self.fellows[:3], PersonPage.DPHStatus.ALUMNI, [self.f24])
        self.set_dph(self.fellows[3:6], PersonPage.DPHStatus.ALUMNI, [self.w24])
        self.set_dph(self.fellows[6:9], PersonPage.DPHStatus.CURRENT, [self.f25])
        # An early leaver: alumni, while the rest of their term stays current.
        self.set_dph(self.fellows[9:10], PersonPage.DPHStatus.ALUMNI, [self.f25])
        self.assertEqual(self.slugs(self.ctx(type='alumni', term=self.f24.pk)),
                         sorted(p.slug for p in self.fellows[:3]))
        self.assertEqual(self.slugs(self.ctx(type='alumni', term=self.f25.pk)),
                         [self.fellows[9].slug])
        self.assertEqual(self.slugs(self.ctx(type='current', term=self.f24.pk)), [])

    def test_other_person_listings_unchanged(self):
        # Senior Management & Board keeps Role on the `type` key.
        board = [self.make_person('board-%02d' % i, ['Board Member', 'Expert'])
                 for i in range(5)]
        managers = [self.make_person('manager-%02d' % i, ['Management Team', 'Staff'],
                                     last_name='Manager')
                    for i in range(5)]
        self.set_dph(board + managers, PersonPage.DPHStatus.CURRENT, [self.f24])
        self.set_dph(managers[:1], PersonPage.DPHStatus.ALUMNI, [self.f25])
        board_value = self.listing(card_type='person', person_type='management_board',
                                   facets=['type'], prefix='')
        staff = PersonType.objects.get(name='Staff')
        context = self.ctx(board_value, type=staff.pk)
        facet = self.facet(context, 'type')
        self.assertEqual(facet['label'], 'Role')
        self.assertNotIn('single', facet)
        self.assertEqual(sorted(o['label'] for o in facet['options']), ['Expert', 'Staff'])
        self.assertEqual(self.slugs(context), sorted(p.slug for p in managers))
        self.assertIsNone(self.facet(context, 'term'))
        # DPH Speakers: status and terms on the people change nothing.
        speakers = [self.make_person('speaker-%02d' % i, ['DPH Speaker'])
                    for i in range(10)]
        self.set_dph(speakers[:5], PersonPage.DPHStatus.CURRENT, [self.f24])
        self.set_dph(speakers[5:], PersonPage.DPHStatus.ALUMNI, [self.f25])
        speaker_value = self.listing(card_type='person', person_type='dph_speaker',
                                     facets=['type', 'topic'], prefix='')
        context = self.ctx(speaker_value, type='current', term=self.f24.pk)
        self.assertEqual(context['router_total'], 10)
        self.assertEqual(
            [f['key'] for f in context['router_facets'] if f['key'] in ('type', 'term')], [])
        # The staff directory keeps Last Name (plus Topic when enabled).
        staff_value = self.listing(card_type='staff', facets=['topic'], prefix='')
        context = self.ctx(staff_value, letter='M')
        self.assertEqual([f['key'] for f in context['router_facets']], ['letter'])
        self.assertEqual(context['router_total'], 5)

    def test_dph_listing_prefix_is_stable(self):
        # The anchor the DPH crumbs deep-link to (BugHerd #516).
        self.assertEqual(default_listing_prefix(self.value), 'r78edfd')

    def test_person_page_admin_has_dph_fields(self):
        panel = next(p for p in PersonPage.content_panels
                     if isinstance(p, MultiFieldPanel) and p.heading == 'DPH Fields')
        fields = [child.field_name for child in panel.children]
        self.assertIn('dph_status', fields)
        self.assertIn('dph_terms', fields)
        # The editor renders both, terms as checkboxes; CIGI manages the terms.
        from django.contrib.auth import get_user_model
        self.client.force_login(get_user_model().objects.create_superuser(
            username='editor', password=None))
        response = self.client.get(
            reverse('wagtailadmin_pages:edit', args=[self.fellows[0].pk]))
        self.assertContains(response, 'name="dph_status"')
        self.assertContains(
            response, 'type="checkbox" name="dph_terms" value="%s"' % self.f25.pk)
        response = self.client.get(reverse('wagtailsnippets_people_dphterm:list'))
        self.assertContains(response, 'Fall 2025')

    def make_hub(self):
        tab = {'type': 'item', 'id': str(uuid.uuid4()), 'value': {
            'label': 'Current Cohort and Alumni',
            'content': [{'type': 'faceted_listing', 'value': self.value}]}}
        return self.home.add_child(instance=BasicPage(
            title='Digital Policy Hub', slug='digital-policy-hub',
            body=[{'type': 'composable_tabs', 'value': {'heading': '', 'tabs': [tab]}}]))

    def test_hub_renders_type_and_term_only_with_data(self):
        hub = self.make_hub()
        url = hub.url + '?tab=current-cohort-and-alumni'
        type_radio = 'name="%s-type" value="current"' % self.prefix
        term_label = '<summary class="ds-router__facet-label">Term</summary>'
        response = self.client.get(url)
        self.assertContains(response, 'id="router-%s"' % self.prefix)
        self.assertContains(response, '<summary class="ds-router__facet-label">Topic</summary>')
        self.assertNotContains(response, '<summary class="ds-router__facet-label">Cohort</summary>')
        self.assertNotContains(response, type_radio)
        self.assertNotContains(response, term_label)
        self.set_dph(self.fellows[:4], PersonPage.DPHStatus.CURRENT, [self.f25])
        self.set_dph(self.fellows[4:8], PersonPage.DPHStatus.ALUMNI, [self.f24])
        response = self.client.get(url)
        self.assertContains(response, type_radio)
        self.assertContains(response, 'type="radio" name="%s-type" value=""' % self.prefix)
        self.assertContains(response, term_label)
        self.assertContains(response, 'name="%s-term" value="%s"' % (self.prefix, self.f25.pk))


class HeroProgramEyebrowTests(TestCase):
    """A topic-less page's hero pills fall back to its theme-mapped programs
    only — a legacy program no longer draws a grey pill (Tim, BugHerd #514;
    cards since #326). Staging's 23832 shape: no topics, programs "Space
    Governance 4.0" (unmapped) + "Space Governance" (Security theme)."""

    @classmethod
    def setUpTestData(cls):
        cls.home = HomePage.objects.get()
        cls.theme = cls.home.add_child(instance=ThemePage(
            title='Digitalization, Security and Democracy', slug='dsd', accent='security'))
        cls.mapped = cls.home.add_child(instance=ProjectPage(
            title='Space Governance', slug='space-governance', publishing_date=timezone.now()))
        cls.legacy = cls.home.add_child(instance=ProjectPage(
            title='Space Governance 4.0', slug='space-governance-4',
            publishing_date=timezone.now()))
        ThemeProgram.objects.create(theme=cls.theme, program=cls.mapped)
        cls.topic = cls.home.add_child(instance=TopicPage(
            title='Climate Change', slug='climate-change'))  # archived-style: no theme
        cls.policy_briefs = cls.home.add_child(instance=PublicationTypePage(
            title='Policy Briefs', slug='policy-briefs'))

    def make_publication(self, slug, projects=(), topics=()):
        page = self.home.add_child(instance=PublicationPage(
            title=slug, slug=slug, publishing_date=timezone.now(),
            publication_type=self.policy_briefs))
        page.projects.set(projects)
        page.topics.set(topics)
        page.save()
        return PublicationPage.objects.get(pk=page.pk)

    def mapped_pill(self):
        return {'title': 'Space Governance', 'url': '/space-governance/', 'accent': 'olive'}

    def test_legacy_program_drops_beside_a_mapped_one(self):
        page = self.make_publication('mixed', projects=[self.legacy, self.mapped])
        self.assertEqual(_topic_eyebrow(page), [self.mapped_pill()])
        self.assertEqual(hero_data(page)['eyebrow'], [self.mapped_pill()])
        response = self.client.get(page.url)
        self.assertContains(response, 'ds-hero__pills', count=1)
        self.assertContains(response, 'class="ds-tag ', count=1)
        self.assertContains(
            response, '<span class="ds-tag ds-surface--accent-olive"><span class="ds-tag__dot" '
            'aria-hidden="true"></span><span class="ds-tag__label">Space Governance</span></span>',
            count=1, html=False)

    def test_only_legacy_programs_render_no_pill_row(self):
        page = self.make_publication('legacy-only', projects=[self.legacy])
        self.assertEqual(hero_data(page)['eyebrow'], [])
        response = self.client.get(page.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'ds-hero__pills')
        self.assertNotContains(response, 'ds-surface--accent-grey')

    def test_topics_win_and_programs_are_not_consulted(self):
        # Unchanged: topic pills keep precedence, and an unmapped topic keeps
        # its grey (the legacy-topic state, Tia 09-18) — only programs filter.
        page = self.make_publication(
            'with-topic', projects=[self.mapped, self.legacy], topics=[self.topic])
        self.assertEqual(_topic_eyebrow(page), [
            {'title': 'Climate Change', 'url': '/climate-change/', 'accent': 'grey'}])

    def test_mapped_program_alone_is_unchanged(self):
        page = self.make_publication('mapped-only', projects=[self.mapped])
        self.assertEqual(_topic_eyebrow(page), [self.mapped_pill()])
