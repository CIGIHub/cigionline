"""Content-hero breadcrumbs (BugHerd #279).

A content single (article, publication incl. books, multimedia, event) tagged
to a current program trails Home > Theme > Program; every other one trails
Home > <archive page title>. No crumb links a TopicPage. The archive page is
Settings -> Archive, else the oldest live BasicPage carrying an archive-mode
Faceted Listing, else the hero keeps its tree trail (core.archive).

Builds its own pages; core/tests.py is not touched.
"""

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from wagtail.models import Page

from articles.models import ArticlePage, ArticleTypePage
from events.models import EventListPage, EventPage
from home.models import HomePage
from multimedia.models import MultimediaListPage, MultimediaPage, MultimediaSeriesPage
from publications.models import PublicationListPage, PublicationPage, PublicationTypePage
from research.models import ProjectPage, ThemePage, ThemeProgram, TopicPage
from streams.blocks import FacetedListingBlock

from .archive import archive_target, clear_cache
from .heroes import hero_data
from .models import BasicPage
from .models_settings import ArchiveSettings

HOME = {'title': 'Home', 'url': '/'}


def archive_listing():
    # The full value an editor's save stores, as on staging page 23872.
    block = FacetedListingBlock()
    return block.get_prep_value(block.to_python({
        'card_type': 'resource', 'program_source': 'none', 'prefix': '',
        'heading': 'Browse All Archived Topics'}))


class ContentBreadcrumbTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.home = HomePage.objects.get()
        # Publishing the archive page fires the notification signal's owner read.
        cls.owner = get_user_model().objects.create_user(
            username='editor', email='editor@example.com', first_name='Ed', last_name='Itor')
        cls.theme = cls.home.add_child(instance=ThemePage(
            title='Digitalization, Security and Democracy', slug='dsd', accent='security'))
        cls.program = cls.home.add_child(instance=ProjectPage(
            title='Space Governance', slug='space-governance', publishing_date=timezone.now()))
        ThemeProgram.objects.create(theme=cls.theme, program=cls.program)
        cls.legacy = cls.home.add_child(instance=ProjectPage(
            title='Space Governance 4.0', slug='space-governance-4', publishing_date=timezone.now()))
        cls.topic = cls.home.add_child(instance=TopicPage(
            title='Emerging Technologies', slug='emerging-technologies'))
        cls.policy_briefs = cls.home.add_child(instance=PublicationTypePage(
            title='Policy Briefs', slug='policy-briefs'))
        cls.books = cls.home.add_child(instance=PublicationTypePage(title='Books', slug='books'))
        cls.opinion = cls.home.add_child(instance=ArticleTypePage(title='Opinion', slug='opinion'))
        cls.cigi_news = cls.home.add_child(instance=ArticleTypePage(
            title='CIGI News', slug='cigi-news-type'))
        cls.publications = cls.home.add_child(instance=PublicationListPage(
            title='Publications', slug='publications'))
        cls.events = cls.home.add_child(instance=EventListPage(title='Events', slug='events'))
        cls.multimedia = cls.home.add_child(instance=MultimediaListPage(
            title='Multimedia', slug='multimedia'))
        cls.series = cls.home.add_child(instance=MultimediaSeriesPage(
            title='Big Tech', slug='big-tech', publishing_date=timezone.now()))
        cls.archive = cls.home.add_child(instance=BasicPage(
            title='Archived Topics', slug='archived-topics', owner=cls.owner,
            body=[{'type': 'faceted_listing', 'value': archive_listing()}]))

    def setUp(self):
        # The lookup is a process cache; never let one test's archive leak.
        clear_cache()
        self.addCleanup(clear_cache)

    # -- builders ---------------------------------------------------------

    def tag(self, page, projects=(), topics=()):
        page.projects.set(projects)
        page.topics.set(topics)
        page.save()  # ParentalManyToMany: set() persists on save
        return page.__class__.objects.get(pk=page.pk)

    def publication(self, slug, publication_type=None, **tags):
        page = self.publications.add_child(instance=PublicationPage(
            title=slug, slug=slug, publishing_date=timezone.now(),
            publication_type=publication_type or self.policy_briefs))
        return self.tag(page, **tags)

    def article(self, slug, article_type=None, **tags):
        page = self.home.add_child(instance=ArticlePage(
            title=slug, slug=slug, publishing_date=timezone.now(),
            article_type=article_type or self.opinion))
        return self.tag(page, **tags)

    def event(self, slug, **tags):
        page = self.events.add_child(instance=EventPage(
            title=slug, slug=slug, publishing_date=timezone.now()))
        return self.tag(page, **tags)

    def multimedia_page(self, slug, parent=None, **fields):
        tags = {k: fields.pop(k) for k in ('projects', 'topics') if k in fields}
        page = (parent or self.multimedia).add_child(instance=MultimediaPage(
            title=slug, slug=slug, publishing_date=timezone.now(), **fields))
        return self.tag(page, **tags)

    def crumbs(self, page, **kwargs):
        return hero_data(page, **kwargs)['breadcrumb']

    def archive_trail(self, title='Archived Topics', url='/archived-topics/'):
        return [HOME, {'title': title, 'url': url}]

    def owned_trail(self):
        return [HOME, {'title': self.theme.title, 'url': '/dsd/'},
                {'title': self.program.title, 'url': '/space-governance/'}]

    def publish(self, page):
        page.save_revision(user=self.owner).publish()

    # -- the rule ---------------------------------------------------------

    def test_program_tagged_singles_keep_theme_program_trail(self):
        for page in (self.publication('owned-pub', projects=[self.program], topics=[self.topic]),
                     self.publication('owned-book', publication_type=self.books,
                                      projects=[self.program]),
                     self.article('owned-article', projects=[self.program]),
                     self.event('owned-event', projects=[self.program]),
                     self.multimedia_page('owned-video', projects=[self.program])):
            with self.subTest(page=page.slug):
                self.assertEqual(self.crumbs(page), self.owned_trail())

    def test_topic_only_publication_trails_to_archive_not_topic(self):
        # #279's paper (23725): today "Home > Emerging Technologies > Resources",
        # linking the unstyled TopicPage.
        page = self.publication('the-macroeconomics-of-canadian-space', topics=[self.topic])
        self.assertEqual(self.crumbs(page), self.archive_trail())

    def test_legacy_program_only_publication_trails_to_archive(self):
        # Was "Home > <legacy program> > Research".
        page = self.publication('legacy-only', projects=[self.legacy])
        self.assertEqual(self.crumbs(page), self.archive_trail())

    def test_untagged_singles_trail_to_archive(self):
        for page in (self.publication('untagged-pub'),
                     self.publication('untagged-book', publication_type=self.books),
                     self.article('untagged-article'),
                     self.event('untagged-event'),
                     self.multimedia_page('untagged-video', multimedia_type='video'),
                     self.multimedia_page('untagged-podcast', multimedia_type='audio')):
            with self.subTest(page=page.slug):
                self.assertEqual(self.crumbs(page), self.archive_trail())

    def test_book_uses_the_book_hero(self):
        page = self.publication('book', publication_type=self.books, topics=[self.topic])
        data = hero_data(page)
        self.assertIn('book', data)
        self.assertEqual(data['breadcrumb'], self.archive_trail())

    def test_cigi_news_article_trails_to_archive(self):
        # News types follow the decided rule (research Option D not taken).
        page = self.article('news-release', article_type=self.cigi_news, topics=[self.topic])
        self.assertEqual(self.crumbs(page), self.archive_trail())
        self.assertFalse(hero_data(page)['banner'])  # still the news hero

    def test_event_registration_hero_has_no_crumb(self):
        self.assertEqual(self.crumbs(self.event('reg'), variant='registration'), [])

    def test_episode_under_live_series_keeps_series_crumb(self):
        episode = self.multimedia_page('episode-1', parent=self.series, multimedia_type='audio',
                                       multimedia_series=self.series)
        self.assertEqual(self.crumbs(episode), [HOME, {'title': 'Big Tech', 'url': '/big-tech/'}])
        # Ownership still wins for a tagged episode.
        tagged = self.multimedia_page('episode-2', parent=self.series, multimedia_type='audio',
                                      projects=[self.program])
        self.assertEqual(self.crumbs(tagged), self.owned_trail())

    def test_series_fk_alone_does_not_make_an_episode(self):
        # 551 videos under /multimedia/ point at an old series by FK only.
        video = self.multimedia_page('old-series-video', multimedia_type='video',
                                     multimedia_series=self.series)
        self.assertEqual(self.crumbs(video), self.archive_trail())

    def test_episode_under_unpublished_series_trails_to_archive(self):
        hidden = self.home.add_child(instance=MultimediaSeriesPage(
            title='Hidden Series', slug='hidden-series', live=False,
            publishing_date=timezone.now()))
        episode = self.multimedia_page('hidden-episode', parent=hidden, multimedia_type='audio')
        self.assertEqual(self.crumbs(episode), self.archive_trail())

    def test_other_heroes_keep_their_trails(self):
        self.assertEqual(self.crumbs(self.program), [HOME, {'title': self.theme.title, 'url': '/dsd/'}])
        self.assertEqual(self.crumbs(self.archive),
                         [HOME, {'title': 'Archived Topics', 'current': True}])
        self.assertEqual(self.crumbs(self.series),
                         [HOME, {'title': 'Big Tech', 'current': True}])
        self.assertEqual(self.crumbs(self.theme),
                         [HOME, {'title': self.theme.title, 'current': True}])

    def test_no_crumb_links_a_topic_page(self):
        pages = [
            self.publication('p-topic', topics=[self.topic]),
            self.publication('p-topic-legacy', topics=[self.topic], projects=[self.legacy]),
            self.publication('b-topic', publication_type=self.books, topics=[self.topic]),
            self.article('a-topic', topics=[self.topic]),
            self.article('n-topic', article_type=self.cigi_news, topics=[self.topic]),
            self.event('e-topic', topics=[self.topic]),
            self.multimedia_page('m-topic', topics=[self.topic]),
            self.multimedia_page('s-topic', parent=self.series, multimedia_type='audio',
                                 topics=[self.topic]),
        ]
        by_url = {p.url: p.specific_class for p in Page.objects.filter(depth__gt=1)}
        for archive_state in ('archive', 'no archive'):
            if archive_state == 'no archive':
                self.archive.unpublish()
            for page in pages:
                with self.subTest(page=page.slug, state=archive_state):
                    for crumb in self.crumbs(page):
                        self.assertIsNot(by_url.get(crumb.get('url')), TopicPage, crumb)

    def test_rendered_publication_crumb(self):
        page = self.publication('rendered', topics=[self.topic])
        response = self.client.get(page.url)
        self.assertContains(
            response, '<a class="ds-breadcrumbs__crumb" href="/archived-topics/" '
            'title="Archived Topics">Archived Topics</a>', html=True)
        self.assertNotContains(response, 'href="/emerging-technologies/" title="Emerging')
        self.assertNotContains(response, '>Resources<')

    # -- finding the archive page -----------------------------------------

    def test_setting_wins_over_auto_detect(self):
        chosen = self.home.add_child(instance=BasicPage(title='Research Archive', slug='library'))
        settings = ArchiveSettings.load()
        settings.archive_page = chosen
        settings.save()
        self.assertEqual(self.crumbs(self.publication('pub')),
                         self.archive_trail('Research Archive', '/library/'))

    def test_blank_setting_auto_detects(self):
        self.assertIsNone(ArchiveSettings.load().archive_page)
        self.assertEqual(archive_target(), {'title': 'Archived Topics', 'url': '/archived-topics/'})

    def test_setting_to_unpublished_page_falls_back_to_auto_detect(self):
        draft = self.home.add_child(instance=BasicPage(title='Draft Archive', slug='draft', live=False))
        settings = ArchiveSettings.load()
        settings.archive_page = draft
        settings.save()
        self.assertEqual(self.crumbs(self.publication('pub')), self.archive_trail())

    def test_oldest_archive_mode_page_wins(self):
        self.home.add_child(instance=BasicPage(
            title='Archive copy', slug='archive-copy',
            body=[{'type': 'faceted_listing', 'value': archive_listing()}]))
        self.assertEqual(archive_target()['url'], '/archived-topics/')

    def test_listing_in_another_mode_is_not_an_archive(self):
        self.archive.unpublish()
        block = FacetedListingBlock()
        listing = block.get_prep_value(block.to_python(
            {'card_type': 'resource', 'program_source': 'page', 'prefix': ''}))
        self.home.add_child(instance=BasicPage(
            title='Program listing', slug='program-listing',
            body=[{'type': 'faceted_listing', 'value': listing}]))
        self.assertIsNone(archive_target())

    def test_no_archive_page_keeps_tree_trail(self):
        self.archive.unpublish()
        self.assertEqual(self.crumbs(self.publication('pub', topics=[self.topic])),
                         [HOME, {'title': 'Publications', 'url': '/publications/'}])
        self.assertEqual(self.crumbs(self.event('ev')),
                         [HOME, {'title': 'Events', 'url': '/events/'}])
        self.assertEqual(self.crumbs(self.multimedia_page('mm')),
                         [HOME, {'title': 'Multimedia', 'url': '/multimedia/'}])
        self.assertEqual(self.crumbs(self.article('art')),
                         [HOME, {'title': 'art', 'current': True}])

    # -- cache --------------------------------------------------------------

    def test_cached_lookup_costs_no_queries(self):
        archive_target()
        with self.assertNumQueries(0):
            archive_target()

    def test_publication_hero_query_count_with_warm_cache(self):
        page = self.publication('counted', topics=[self.topic])
        hero_data(page)  # warm the archive lookup
        with CaptureQueriesContext(connection) as ctx:
            hero_data(page)
        self.assertFalse([q for q in ctx.captured_queries
                          if 'core_archivesettings' in q['sql'] or '"body" @>' in q['sql']])
        # Trail: the page's programs (1; none, so no ThemeProgram query) and
        # the cached archive (0). The rest is the hero's own: eyebrow topics,
        # site root paths (URLs), authors (2), editors. Before #279 the trail
        # also re-ran the ownership check and read topics + programs again.
        with self.assertNumQueries(6):
            hero_data(page)

    def test_cache_clears_when_archive_page_is_renamed(self):
        page = self.publication('pub')
        self.assertEqual(self.crumbs(page), self.archive_trail())   # warm
        self.archive.title = 'Research Archive'
        self.publish(self.archive)
        self.assertEqual(self.crumbs(page), self.archive_trail('Research Archive'))

    def test_cache_clears_when_archive_page_is_unpublished(self):
        page = self.publication('pub')
        self.assertEqual(self.crumbs(page), self.archive_trail())   # warm
        self.archive.unpublish()
        self.assertEqual(self.crumbs(page), [HOME, {'title': 'Publications', 'url': '/publications/'}])

    def test_cache_clears_when_setting_is_saved(self):
        page = self.publication('pub')
        self.assertEqual(self.crumbs(page), self.archive_trail())   # warm
        chosen = self.home.add_child(instance=BasicPage(title='Library', slug='library'))
        settings = ArchiveSettings.load()
        settings.archive_page = chosen
        settings.save()
        self.assertEqual(self.crumbs(page), self.archive_trail('Library', '/library/'))

    def test_cache_clears_when_archive_page_moves(self):
        page = self.publication('pub')
        self.assertEqual(self.crumbs(page), self.archive_trail())   # warm
        about = self.home.add_child(instance=BasicPage(title='About', slug='about'))
        Page.objects.get(pk=self.archive.pk).move(about, pos='last-child')
        self.assertEqual(self.crumbs(page),
                         self.archive_trail(url='/about/archived-topics/'))
