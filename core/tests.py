import shutil
import tempfile
import uuid
from datetime import date
from types import SimpleNamespace
from unittest.mock import Mock, patch

from articles.models import ArticleListPage, ArticlePage, ArticleTypePage
from django import forms
from annual_reports.models import AnnualReportListPage
from careers.models import JobPostingListPage
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.template.loader import get_template, render_to_string
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
from streams.blocks import AnniversaryVideoTextBlock, FacetedListingBlock, VideoTextBlock
from wagtail.admin.panels import MultiFieldPanel
from wagtail.blocks import StructValue
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import PageViewRestriction, Site
from wagtail.test.utils import WagtailPageTestCase

from .faceted_listing import build_listing_context, default_listing_prefix, is_leadership_listing
from .heroes import _topic_eyebrow, hero_data, person_hero_data
from .wagtail_hooks import get_filter_purge_cache_urls, get_purge_cache_url
from .models import (
    BasicPage,
    ContentPageAuthor,
    FacilityRentalsPage,
    FundingPage,
    PrivacyNoticePage,
    Theme,
    TwentyFifthFeatureLandingPage,
    TwentyFifthPageSingleton,
    TwentiethPage,
    TwentiethPageSingleton,
)


class PurgeCloudflareCacheTests(WagtailPageTestCase):
    def setUp(self):
        Site.clear_site_root_paths_cache()
        self.addCleanup(Site.clear_site_root_paths_cache)
        Site.objects.update(hostname='www.cigionline.org', port=443)

    def test_get_purge_cache_url_accepts_full_urls(self):
        url = 'https://www.cigionline.org/articles/example/'

        self.assertEqual(get_purge_cache_url(url), url)

    def test_get_purge_cache_url_uses_default_site_for_paths(self):
        self.assertEqual(
            get_purge_cache_url('/articles/example/'),
            'https://www.cigionline.org/articles/example/',
        )

    def test_get_purge_cache_url_ignores_blank_lines(self):
        self.assertIsNone(get_purge_cache_url('   '))

    def test_get_purge_cache_url_rejects_invalid_input(self):
        with self.assertRaises(forms.ValidationError):
            get_purge_cache_url('articles/example/')

    def test_get_purge_cache_url_rejects_non_http_urls(self):
        with self.assertRaises(forms.ValidationError):
            get_purge_cache_url('ftp://www.cigionline.org/articles/example/')

    def test_get_filter_purge_cache_urls_filters_articles_by_theme_and_article_type(self):
        home_page = HomePage.objects.get()

        article_list = ArticleListPage(title='Opinions')
        home_page.add_child(instance=article_list)

        article_type = ArticleTypePage(title='Op-Eds')
        article_list.add_child(instance=article_type)

        theme = Theme.objects.create(name='Policy Prompt')
        matching_article = ArticlePage(
            title='Matching Article',
            article_type=article_type,
            theme=theme,
            publishing_date=timezone.now(),
        )
        article_list.add_child(instance=matching_article)

        other_article = ArticlePage(
            title='Other Article',
            article_type=article_type,
            publishing_date=timezone.now(),
        )
        article_list.add_child(instance=other_article)
        restricted_article = article_list.add_child(instance=ArticlePage(
            title='Restricted Article',
            article_type=article_type,
            theme=theme,
            publishing_date=timezone.now(),
        ))
        PageViewRestriction.objects.create(
            page=restricted_article,
            restriction_type=PageViewRestriction.PASSWORD,
            password='secret',
        )

        urls = get_filter_purge_cache_urls({
            'page_types': ['articles.ArticlePage'],
            'themes': [theme],
            'article_types': [article_type],
        })

        self.assertEqual(urls, [matching_article.get_full_url()])

    def test_view_requires_admin_access(self):
        from django.contrib.auth import get_user_model

        self.client.force_login(get_user_model().objects.create_user(
            username='staff', password=None, is_staff=True))

        response = self.client.get(reverse('purge_cloudflare_cache'))

        self.assertEqual(response.status_code, 302)

    @override_settings(WAGTAILFRONTENDCACHE={'cloudflare': {}})
    @patch('core.wagtail_hooks.purge_urls_from_cache')
    def test_preview_does_not_purge(self, purge_mock):
        from django.contrib.auth import get_user_model

        self.client.force_login(get_user_model().objects.create_superuser(
            username='admin', password=None))

        response = self.client.post(
            reverse('purge_cloudflare_cache'),
            {'pages': 'https://www.cigionline.org/example/', 'preview': '1'},
        )

        self.assertEqual(response.status_code, 200)
        purge_mock.assert_not_called()

    @override_settings(WAGTAILFRONTENDCACHE={'cloudflare': {}})
    @patch('core.wagtail_hooks.purge_urls_from_cache')
    def test_purge_deduplicates_urls(self, purge_mock):
        from django.contrib.auth import get_user_model

        self.client.force_login(get_user_model().objects.create_superuser(
            username='admin', password=None))
        url = 'https://www.cigionline.org/example/'

        response = self.client.post(
            reverse('purge_cloudflare_cache'),
            {'pages': f'{url}\n{url}'},
        )

        self.assertEqual(response.status_code, 200)
        purge_mock.assert_called_once_with([url])


class BasicPageTests(WagtailPageTestCase):
    def test_related_file_icons_match_document_type(self):
        template = get_template('includes/core_related_files_table.html')

        for filename, icon in (
            ('report.pdf', 'fa-file-pdf'),
            ('report.doc', 'fa-file-word'),
            ('report.DOCX', 'fa-file-word'),
            ('slides.ppt', 'fa-file-powerpoint'),
            ('slides.PPTX', 'fa-file-powerpoint'),
            ('files.ZIP', 'fa-file-zipper'),
        ):
            with self.subTest(filename=filename):
                document = SimpleNamespace(url=filename, title='Report', file_size=1)
                html = template.render({
                    'file_blocks': [SimpleNamespace(value=document)],
                })

                self.assertIn(icon, html)

    def test_body_includes_interactive_chart(self):
        body = BasicPage._meta.get_field('body')

        self.assertIn('interactive_chart', body.stream_block.child_blocks)

    def test_dph_page_uses_design_system_application_notice(self):
        home = HomePage.objects.get()
        dph_theme, _ = Theme.objects.get_or_create(name='DPH')
        page = home.add_child(instance=BasicPage(
            title='Digital Policy Hub',
            slug='digital-policy-hub',
            theme=dph_theme,
        ))

        self.assertEqual(page.get_template(RequestFactory().get(page.url)), 'core/basic_page.html')
        response = self.client.get(page.url)
        self.assertContains(response, 'Applications for the Digital Policy Hub are now being accepted')
        self.assertContains(response, 'href="/careers/dph-call-for-applications-2027/"')
        self.assertContains(response, '>Apply Now<')

    def test_dph_application_notice_follows_authored_hero(self):
        home = HomePage.objects.get()
        page = home.add_child(instance=BasicPage(
            title='Digital Policy Hub',
            slug='digital-policy-hub',
            body=[{
                'type': 'primary_hero',
                'value': {
                    'surface': 'charcoal',
                    'accent': 'green',
                    'heading': 'DPH Hero',
                    'description': '',
                },
            }],
        ))

        response = self.client.get(page.url)
        content = response.content.decode()
        self.assertContains(response, 'dph-application-heading', count=2)
        self.assertLess(content.index('DPH Hero'), content.index('dph-application-heading'))

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
            {
                AnnualReportListPage,
                BasicPage,
                FacilityRentalsPage,
                FundingPage,
                PersonListPage,
                ProjectPage,
                TwentiethPage,
                TwentiethPageSingleton,
            }
        )


class TwentyFifthPageSingletonTests(WagtailPageTestCase):
    def test_twentyfifthpagesingleton_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            TwentyFifthPageSingleton,
            {HomePage},
        )

    def test_twentyfifthpagesingleton_child_page_types(self):
        self.assertAllowedSubpageTypes(
            TwentyFifthPageSingleton,
            {TwentyFifthFeatureLandingPage},
        )

    def test_anniversary_body_uses_legacy_video_shape_without_replacing_ds_block(self):
        body = TwentyFifthPageSingleton._meta.get_field('body').stream_block

        self.assertIsInstance(body.child_blocks['video_text'], AnniversaryVideoTextBlock)
        self.assertIn('paragraph', body.child_blocks['video_text'].child_blocks)
        self.assertIn('heading', VideoTextBlock().child_blocks)

    @override_settings(DEBUG=False)
    @patch('utils.security.verify_turnstile_token', return_value=False)
    def test_ajax_subscription_rejects_failed_turnstile(self, verify_turnstile_token):
        request = RequestFactory().post(
            '/',
            {'anniversary_newsletter_form': '1'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        response = TwentyFifthPageSingleton(title='Anniversary').serve(request)

        self.assertEqual(response.status_code, 400)
        verify_turnstile_token.assert_called_once()

    def test_anniversary_templates_compile(self):
        for template in (
            'core/twenty_fifth_page_singleton.html',
            'core/twenty_fifth_feature_landing_page.html',
            'streams/anniversary_video_text_block.html',
            'streams/founder_letter_block.html',
        ):
            get_template(template)


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


class CardPlaceholderTests(SimpleTestCase):
    PLACEHOLDER = 'assets/CIGI-default-recommended-thumb'

    def render(self, variant, show_media):
        return render_to_string('includes/card.html', {
            'variant': variant,
            'show_media': show_media,
            'image': None,
            'pills': [],
            'title': 'Card title',
            'url': '/card/',
            'excerpt': '',
        })

    def test_image_card_variants_use_placeholder_without_an_authored_image(self):
        for variant in ('media-vertical', 'media-compact', 'media-stacked',
                        'resource-feature'):
            with self.subTest(variant=variant):
                self.assertIn(self.PLACEHOLDER, self.render(variant, show_media=True))

    def test_text_only_card_variants_do_not_use_placeholder(self):
        for variant in ('article-list-row', 'event', 'resource-compact'):
            with self.subTest(variant=variant):
                self.assertNotIn(self.PLACEHOLDER, self.render(variant, show_media=False))

    def test_compact_opinion_remains_deliberately_text_only(self):
        from core.cards import card_data

        page = SimpleNamespace(
            title='Opinion', feature_title='', feature_subtitle='', subtitle='',
            short_description='', image_feature=None, image_hero=None,
            article_type=SimpleNamespace(slug='opinion'), contenttype='Opinion',
            contentsubtype='Opinion', publishing_date=None,
        )
        page.specific = page
        page.get_url = lambda request=None: '/opinion/'

        self.assertFalse(card_data(page, variant='media-compact', pills=[])['show_media'])


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


class LeadershipListingSelectionTests(SimpleTestCase):
    def test_only_the_target_tab_listing_is_selected(self):
        target = {'card_type': 'person', 'person_type': 'management_board', 'prefix': 'leaders'}
        other = {**target, 'prefix': 'other'}
        child = lambda value: SimpleNamespace(block_type='faceted_listing', value=value)
        tabs = [
            {'label': 'Other People', 'content': [child(other)]},
            {'label': 'Senior Management and Board of Directors', 'content': [child(target)]},
        ]
        page = SimpleNamespace(slug='leadership-partners-and-team', body=[
            SimpleNamespace(block_type='composable_tabs', value={'tabs': tabs})])
        self.assertTrue(is_leadership_listing(page, target, 'leaders'))
        self.assertFalse(is_leadership_listing(page, other, 'other'))
        page.slug = 'different-page'
        self.assertFalse(is_leadership_listing(page, target, 'leaders'))

    def test_leadership_item_with_and_without_photo(self):
        person = PersonPage(content_type_id=1, title='A Leader', position='Director',
                            short_bio='<p>Full <strong>biography</strong>. '
                                      '<a href="https://example.com">More</a></p>')
        with patch.object(person, 'get_url', return_value='/leader/'):
            html = render_to_string('includes/router_items/leadership.html', {'item': person})
            self.assertIn('ds-leadership-person__photo--default', html)
            self.assertIn('A Leader', html)
            self.assertIn('Director', html)
            self.assertIn('Full <strong>biography</strong>', html)
            self.assertIn('href="https://example.com"', html)
            self.assertEqual(html.count('href="/leader/"'), 1)
            self.assertIn('ds-expert-card__name ds-leadership-person__name', html)
            self.assertNotIn('<img', html)

            image = get_image_model()(title='Portrait', collection_id=1)
            person.image_square = image
            rendition = Mock()
            rendition.img_tag.return_value = '<img src="/portrait.jpg" alt="Portrait">'
            with patch.object(image, 'get_rendition', return_value=rendition):
                html = render_to_string('includes/router_items/leadership.html', {'item': person})
            self.assertIn('src="/portrait.jpg"', html)
            self.assertIn('ds-expert-card__avatar ds-leadership-person__photo', html)
            self.assertEqual(html.count('href="/leader/"'), 1)
            self.assertNotIn('ds-leadership-person__photo--default', html)


class LeadershipListingPresentationTests(TestCase):
    @classmethod
    def setUpClass(cls):
        media_root = tempfile.mkdtemp(prefix='leadership-tests-')
        cls.addClassCleanup(shutil.rmtree, media_root, ignore_errors=True)
        cls.enterClassContext(override_settings(MEDIA_ROOT=media_root))
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        home = HomePage.objects.get()
        people = home.add_child(instance=PeoplePage(title='People', slug='people'))
        image = get_image_model().objects.create(
            title='Portrait', file=get_test_image_file(filename='portrait.png'))
        board = PersonType.objects.get(name='Board Member')
        management = PersonType.objects.get(name='Management Team')
        staff = PersonType.objects.get(name='Staff')
        expert = PersonType.objects.get(name='Expert')
        for i in range(14):
            person = people.add_child(instance=PersonPage(
                title='Leader %02d' % i, slug='leader-%02d' % i,
                first_name='Leader', last_name='%02d' % i,
                person_weight=5 if i in (1, 2) else 0,
                position='Director', short_bio='<p>Full <strong>biography</strong>.</p>',
                image_square=image if i == 0 else None))
            types = [board, staff if i < 13 else expert]
            if i < 3:
                types.append(management)
            person.person_types.set(types)
            person.save()
        cls.staff_id = staff.pk
        block = FacetedListingBlock()

        def listing(prefix):
            return block.get_prep_value(block.to_python({
                'card_type': 'person', 'person_type': 'management_board',
                'prefix': prefix, 'show_filters': True, 'show_search': True,
                'facets': ['type'],
            }))

        def tab(label, value):
            return {'type': 'item', 'id': str(uuid.uuid4()), 'value': {
                'label': label, 'content': [{'type': 'faceted_listing', 'value': value}]}}

        cls.page = home.add_child(instance=BasicPage(
            title='Leadership', slug='leadership-partners-and-team',
            body=[{'type': 'composable_tabs', 'value': {'tabs': [
                tab('Other People', listing('other')),
                tab('Senior Management and Board of Directors', listing('leaders')),
            ]}}]))
        cls.other_page = home.add_child(instance=BasicPage(
            title='Other', slug='other-leadership',
            body=[{'type': 'composable_tabs', 'value': {'tabs': [
                tab('Senior Management and Board of Directors', listing('leaders')),
            ]}}]))

    def test_nested_tabs_show_all_people_in_weight_order_without_router_controls(self):
        active = self.client.get(self.page.url, {
            'tab': 'senior-management-and-board-of-directors',
            'leaders-type': str(self.staff_id), 'leaders-page': '2', 'leaders-q': 'absent',
        })
        self.assertContains(active, 'Senior Management')
        self.assertContains(active, 'Board Members')
        self.assertContains(active, 'ds-leadership-person__name')
        self.assertContains(active, 'Director')
        self.assertContains(active, 'Full <strong>biography</strong>')
        self.assertContains(active, 'ds-leadership-person__photo--default')
        self.assertContains(active, 'portrait', status_code=200)
        html = active.content.decode()
        management = html.split('id="leaders-management" role="tabpanel"', 1)[1]
        management, board = management.split('id="leaders-board" role="tabpanel"', 1)
        self.assertLess(management.index('Leader 01'), management.index('Leader 02'))
        self.assertLess(management.index('Leader 02'), management.index('Leader 00'))
        self.assertNotIn('Leader 13', management)
        self.assertLess(board.index('Leader 01'), board.index('Leader 02'))
        self.assertLess(board.index('Leader 02'), board.index('Leader 00'))
        self.assertIn('Leader 13', board)
        self.assertNotIn('data-router-prefix="leaders"', html)
        self.assertNotIn('name="leaders-type"', html)
        self.assertNotIn('name="leaders-q"', html)

    def test_inactive_tab_and_legacy_ajax_return_full_nested_lists(self):
        inactive = self.client.get(self.page.url, {'tab': 'other-people'})
        self.assertContains(inactive, 'id="leaders-management"')
        self.assertContains(inactive, 'id="leaders-board"')
        ajax = self.client.get(self.page.url, {'router': 'leaders', 'leaders-page': '2'},
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = ajax.json()
        self.assertEqual(data['total'], 17)
        self.assertIn('id="leaders-management"', data['html'])
        self.assertIn('id="leaders-board"', data['html'])
        self.assertIn('Leader 13', data['html'])
        self.assertNotIn('ds-router__pager', data['html'])

    def test_other_instances_keep_person_cards(self):
        for page, prefix in ((self.page, 'other'), (self.other_page, 'leaders')):
            response = self.client.get(page.url, {'router': prefix},
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertIn('ds-expert-card', response.json()['html'])
            self.assertNotIn('ds-leadership-person', response.json()['html'])


class DPHCohortListingTests(TestCase):
    """The DPH "Current Cohort and Alumni" listing filters by Type (Current
    Cohort / Alumni), Cohort, and Working Paper theme. Builds its own pages —
    no people.json fixture."""

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
        working_papers = cls.home.add_child(instance=PublicationTypePage(
            title='Working Paper', slug='working-paper'))
        for topic, fellows in ((cls.ai_topic, cls.fellows[1::2]),
                               (cls.data_topic, cls.fellows[::2])):
            paper = cls.home.add_child(instance=PublicationPage(
                title='%s Working Paper' % topic.title,
                slug='%s-working-paper' % topic.slug,
                publishing_date=timezone.now(), publication_type=working_papers))
            paper.topics.set([topic])
            paper.save()
            for fellow in fellows:
                ContentPageAuthor.objects.create(content_page=paper, author=fellow)

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

    def test_no_cohort_data_shows_every_fellow_and_theme(self):
        context = self.ctx()
        self.assertEqual(context['router_total'], 12)
        self.assertEqual([f['key'] for f in context['router_facets']], ['topic'])
        self.assertEqual(self.facet(context, 'topic')['label'], 'Theme')

    def test_theme_comes_from_working_papers_and_filters_with_cohort(self):
        # The person's materialized topics are deliberately wrong: the DPH
        # cohort page follows Working Paper topics, as production did.
        self.fellows[0].derived_topics.set([self.ai_topic])
        self.set_dph(self.fellows[:6], terms=[self.f25])
        facet = self.facet(self.ctx(), 'topic')
        self.assertEqual([option['label'] for option in facet['options']],
                         ['AI and Transformative Technology', 'Data, Economy and Society'])
        context = self.ctx(topic=self.data.pk, term=self.f25.pk)
        self.assertEqual(self.slugs(context),
                         sorted(fellow.slug for fellow in self.fellows[0:6:2]))

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
        self.assertEqual(facet['label'], 'Cohort')
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
        term_label = '<summary class="ds-router__facet-label">Cohort</summary>'
        response = self.client.get(url)
        self.assertContains(response, 'id="router-%s"' % self.prefix)
        self.assertContains(response, '<summary class="ds-router__facet-label">Theme</summary>')
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
