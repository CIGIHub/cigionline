import importlib

from core.models import BasicPage
from wagtail.models import Page
from articles.models import ArticlePage, ArticleTypePage
from django.contrib.auth.models import User
from django.core.management import call_command, CommandError
from django.utils import timezone
from home.models import HomePage, Think7HomePage
from publications.models import PublicationListPage, PublicationPage, PublicationTypePage
from django.template import Context, Template
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import nested_form_data
from utils.helpers import CreatePage, CreateArticlePage
from datetime import date

from .models import (
    ProjectListPage,
    ProjectPage,
    ResearchLandingPage,
    ThemePage,
    ThemeProgram,
    TopicListPage,
    TopicPage,
)


class ProjectListPageTests(WagtailPageTestCase):
    def test_projectlistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            ProjectListPage,
            {HomePage, Think7HomePage},
        )

    def test_projectlistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            ProjectListPage,
            {ProjectPage},
        )


class ProjectPageTests(WagtailPageTestCase):
    def test_projectpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            ProjectPage,
            {BasicPage, ProjectListPage},
        )

    def test_projectpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            ProjectPage,
            {},
        )


class ResearchLandingPageTests(WagtailPageTestCase):
    def test_researchlandingpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            ResearchLandingPage,
            {HomePage},
        )

    def test_researchlandingpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            ResearchLandingPage,
            {},
        )


class TopicListPageTests(WagtailPageTestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='testsuperuser',
            email='testsuperuser@example.com',
            password='testpassword'
        )
        self.client.login(username='testsuperuser', password='testpassword')

    def test_topiclistpage_parent_page_types(self):
        """
        Verify allowed parent page types.
        """
        self.assertAllowedParentPageTypes(
            TopicListPage,
            {HomePage},
        )

    def test_topiclistpage_child_page_types(self):
        """
        Verify allowed child page types.
        """
        self.assertAllowedSubpageTypes(
            TopicListPage,
            {TopicPage},
        )

    def test_can_create_under_homepage(self):
        """
        Test that a TopicListPage can be created as a child of a HomePage.
        """
        home_page = HomePage.objects.get()
        self.assertCanCreate(home_page, TopicListPage, nested_form_data({
            'title': 'Topics',
        }))

    def test_cannot_create_second_topiclistpage(self):
        """
        Test that a TopicListPage cannot be created if a TopicListPage already
        exists.
        """
        home_page = HomePage.objects.get()
        # Create the first TopicListPage
        self.assertCanCreate(home_page, TopicListPage, nested_form_data({
            'title': 'Topics',
        }))
        try:
            self.assertCanCreate(home_page, TopicListPage, nested_form_data({
                'title': 'Topics 2',
            }))
            self.fail('Expected to error')
        except AssertionError as ae:
            if str(ae) == "Creating a page research.topiclistpage didn't redirect the user to the expected page /admin/pages/3/, but to [(\'/admin/\', 302)]":
                pass
            else:
                raise ae


class TopicPageTests(WagtailPageTestCase):
    def test_topicpage_parent_page_types(self):
        """
        Verify allowed parent page types.
        """
        self.assertAllowedParentPageTypes(
            TopicPage,
            {TopicListPage},
        )

    def test_topicpage_child_page_types(self):
        """
        Verify allowed child page types.
        """
        self.assertAllowedSubpageTypes(
            TopicPage,
            {},
        )


class ConsolidateTopicsTests(WagtailPageTestCase):
    def test_program_topic_backfill_is_dry_run_then_idempotent(self):
        home = HomePage.objects.get()
        projects = home.add_child(instance=ProjectListPage(
            title='Programs', slug='programs'))
        program = projects.add_child(instance=ProjectPage(
            title='Next-Generation Economies: Middle Powers in a Changing World',
            slug='next-generation-economies',
            publishing_date=timezone.now(),
        ))
        topics = home.add_child(instance=TopicListPage(title='Topics', slug='topics'))
        topic = topics.add_child(instance=TopicPage(
            title='India, China and Africa', slug='india-china-and-africa'))
        publications = home.add_child(instance=PublicationListPage(
            title='Publications', slug='publications'))
        publication_type = publications.add_child(instance=PublicationTypePage(
            title='Policy Brief', slug='policy-brief'))
        publication = publications.add_child(instance=PublicationPage(
            title='A Current Brief',
            slug='current-brief',
            publishing_date=timezone.now(),
            publication_type=publication_type,
        ))
        publication.projects.add(program)
        publication.save()

        call_command('consolidate_topics')
        self.assertFalse(publication.topics.filter(pk=topic.pk).exists())

        call_command('consolidate_topics', '--apply')
        call_command('consolidate_topics', '--apply')
        self.assertEqual(publication.topics.filter(pk=topic.pk).count(), 1)


class RenameProjectPagesTests(WagtailPageTestCase):
    RENAMES = [
        ('Space Governance 4.0', 'Space Governance'),
        (
            'Strengthening Canada’s National Security in a Complex World',
            'National Security and Cybersecurity',
        ),
        ('Legitimate Influence or Unlawful Manipulation?', 'Freedom of Thought'),
        ('Digital Assets in a Deglobalized World', 'Governance of Digital Money and Assets'),
        (
            'Next-Generation Economies: Middle Powers in a Changing World',
            'Next-Generation Economies',
        ),
        ('Global Economic Scenarios', 'Multilateral and Institutional Reform'),
    ]

    def setUp(self):
        home = HomePage.objects.get()
        self.pages = []
        for index, (old_title, _) in enumerate(self.RENAMES):
            self.pages.append(home.add_child(instance=ProjectPage(
                title=old_title,
                slug=f'legacy-program-{index}',
                publishing_date=timezone.now(),
            )))

    def test_command_is_dry_run_then_idempotent(self):
        call_command('rename_project_pages')
        self.assertEqual(
            set(ProjectPage.objects.filter(pk__in=[page.pk for page in self.pages])
                .values_list('title', flat=True)),
            {old_title for old_title, _ in self.RENAMES},
        )

        call_command('rename_project_pages', '--apply')
        revision_counts = {}
        for index, (page, (_, new_title)) in enumerate(zip(self.pages, self.RENAMES)):
            page.refresh_from_db()
            self.assertEqual(page.title, new_title)
            self.assertEqual(page.slug, f'legacy-program-{index}')
            revision_counts[page.pk] = page.revisions.count()

        call_command('rename_project_pages', '--apply')
        for page in self.pages:
            self.assertEqual(page.revisions.count(), revision_counts[page.pk])

    def test_command_refuses_a_destination_collision_before_writing(self):
        home = HomePage.objects.get()
        home.add_child(instance=ProjectPage(
            title='Space Governance',
            slug='space-governance',
            publishing_date=timezone.now(),
        ))

        with self.assertRaisesMessage(CommandError, 'destination page already exists'):
            call_command('rename_project_pages', '--apply')

        self.assertEqual(
            set(ProjectPage.objects.filter(pk__in=[page.pk for page in self.pages])
                .values_list('title', flat=True)),
            {old_title for old_title, _ in self.RENAMES},
        )

    def test_command_preserves_the_superseded_multilateral_seed(self):
        home = HomePage.objects.get()
        seeded = home.add_child(instance=ProjectPage(
            title='Multilateral and Institutional Reform',
            slug='multilateral-and-institutional-reform',
            publishing_date=timezone.now(),
        ))

        call_command('rename_project_pages', '--apply')

        source = ProjectPage.objects.get(pk=self.pages[-1].pk)
        seeded.refresh_from_db()
        self.assertEqual(source.title, 'Multilateral and Institutional Reform')
        self.assertEqual(source.slug, 'legacy-program-5')
        self.assertEqual(
            seeded.title,
            'Multilateral and Institutional Reform (superseded seed)',
        )
        self.assertEqual(seeded.slug, 'multilateral-and-institutional-reform-superseded')
        self.assertTrue(seeded.url_path.endswith(
            '/multilateral-and-institutional-reform-superseded/'
        ))
        self.assertFalse(seeded.live)


class SeedThemeProgramsMigrationTests(WagtailPageTestCase):
    def test_reuses_legacy_page_as_freedom_of_thought(self):
        from django.apps import apps

        home = HomePage.objects.get()
        theme = home.add_child(instance=ThemePage(
            title='Digitalization, Security and Democracy',
            slug='digitalization-security-democracy',
        ))
        titles = [
            'Supporting Safer Digital Spaces',
            'Space Governance 4.0',
            'Legitimate Influence or Unlawful Manipulation?',
            'Strengthening Canada’s National Security in a Complex World',
        ]
        pages = [
            home.add_child(instance=ProjectPage(
                title=title,
                slug=f'migration-program-{index}',
                publishing_date=timezone.now(),
            ))
            for index, title in enumerate(titles)
        ]

        importlib.import_module('research.migrations.0066_seed_theme_programs').seed(apps, None)
        importlib.import_module('research.migrations.0067_seed_net_new_programs').seed(apps, None)

        rows = list(theme.theme_programs.order_by('sort_order'))
        self.assertEqual([row.program_id for row in rows], [page.pk for page in pages])
        self.assertEqual([row.sort_order for row in rows], [0, 1, 2, 3])
        self.assertEqual(rows[2].label, 'Freedom of Thought')


class WireProgramPagesTests(WagtailPageTestCase):
    def setUp(self):
        home = HomePage.objects.get()
        self.cooperation = home.add_child(instance=ThemePage(
            title='Global Cooperation and Governance',
            slug='global-cooperation-governance',
        ))
        self.programs = []
        for index, title in enumerate([
            'Multilateral and Institutional Reform',
            'Canada-U.S. Relations in the Second Century',
        ]):
            self.programs.append(home.add_child(instance=ProjectPage(
                title=title,
                slug=f'existing-program-{index}',
                publishing_date=timezone.now(),
            )))

    def test_command_only_wires_existing_pages_and_is_idempotent(self):
        page_ids = set(ProjectPage.objects.values_list('pk', flat=True))

        call_command('wire_program_pages')
        call_command('wire_program_pages')

        self.assertEqual(set(ProjectPage.objects.values_list('pk', flat=True)), page_ids)
        self.assertEqual(ThemeProgram.objects.filter(
            program__in=self.programs,
        ).count(), 2)
        self.assertEqual(
            list(ThemeProgram.objects.filter(program__in=self.programs)
                 .order_by('sort_order').values_list('sort_order', flat=True)),
            [1, 2],
        )

    def test_command_fails_before_writing_when_a_page_is_missing(self):
        Page.objects.filter(pk=self.programs[-1].pk).update(
            title='Not the expected program',
            draft_title='Not the expected program',
        )

        with self.assertRaisesMessage(CommandError, 'expected one ProjectPage, found 0'):
            call_command('wire_program_pages')

        self.assertFalse(ThemeProgram.objects.filter(program__in=self.programs[:-1]).exists())


class SeedGlobalCooperationProgramsTests(WagtailPageTestCase):
    def setUp(self):
        self.parent = HomePage.objects.get().add_child(instance=BasicPage(
            title='Programs',
            slug='programs',
        ))

    def test_command_is_dry_run_then_creates_one_draft_idempotently(self):
        call_command('seed_global_cooperation_programs')
        self.assertFalse(ProjectPage.objects.exists())

        call_command('seed_global_cooperation_programs', '--apply')
        call_command('seed_global_cooperation_programs', '--apply')

        pages = ProjectPage.objects.order_by('slug')
        self.assertEqual(pages.count(), 1)
        self.assertEqual(
            set(pages.values_list('title', 'slug')),
            {
                (
                    'Canada-U.S. Relations in the Second Century',
                    'canada-us-relations-in-the-second-century',
                ),
            },
        )
        self.assertFalse(pages.filter(live=True).exists())
        self.assertEqual(
            set(page.get_parent().pk for page in pages),
            {self.parent.pk},
        )

    def test_command_fails_before_writing_on_slug_conflict(self):
        self.parent.add_child(instance=ProjectPage(
            title='Conflicting page',
            slug='canada-us-relations-in-the-second-century',
            publishing_date=timezone.now(),
        ))

        with self.assertRaisesMessage(CommandError, 'sibling slug'):
            call_command('seed_global_cooperation_programs', '--apply')

        self.assertFalse(ProjectPage.objects.filter(
            title='Multilateral and Institutional Reform',
        ).exists())


class HighlightedTopicsTests(WagtailPageTestCase):
    TEMPLATE = Template('{% load topic_tags %} {% highlighted_topics %}')

    def _tag_topic(self, topic_title, article_title):
        CreatePage(Page, 'Articles', 'Home').create_page()
        article_type_page = CreatePage(ArticleTypePage, 'Test', 'Articles').create_page()
        article_page = CreateArticlePage(ArticlePage, article_title, 'Articles', date.today(), article_type_page).create_article_page()
        article_page.topics.add(TopicPage.objects.get(title=topic_title))
        article_page.save()

    def test_if_no_topics_template_should_be_empty(self):
        rendered = self.TEMPLATE.render(Context({}))

        self.assertEqual(' \n\n\n<ul class="highlighted-topics-list">\n  \n</ul>\n', rendered)

    def test_correct_number_of_topics_render(self):
        for n in range(5):
            TopicPage.objects.create(path='/topic{0}'.format(n), depth=1, title='topic{0}'.format(n), slug='topic{0}'.format(n), archive=0, live=True)
            self._tag_topic('topic{0}'.format(n), 'article{0}'.format(n))
        rendered = self.TEMPLATE.render(Context({}))

        self.assertIn('topic0', rendered)
        self.assertIn('topic1', rendered)
        self.assertIn('topic2', rendered)
        self.assertIn('topic3', rendered)
        self.assertIn('topic4', rendered)
        self.assertNotIn('topic5', rendered)

    def test_topics_untagged_do_not_render(self):
        TopicPage.objects.create(path='/topic1', depth=1, title='topic1', slug='topic1', archive=0, live=True)
        rendered = self.TEMPLATE.render(Context({}))

        self.assertNotIn('topic1', rendered)

    def test_topics_not_live_do_not_render(self):
        TopicPage.objects.create(path='/topic1', depth=1, title='topic1', slug='topic1', archive=0, live=False)
        self._tag_topic('topic1', 'article1')
        rendered = self.TEMPLATE.render(Context({}))

        self.assertNotIn('topic1', rendered)

    def test_topics_archived_do_not_render(self):
        TopicPage.objects.create(path='/topic1', depth=1, title='topic1', slug='topic1', archive=1, live=True)
        self._tag_topic('topic1', 'article1')
        rendered = self.TEMPLATE.render(Context({}))

        self.assertNotIn('topic1', rendered)


class TopicsTagTests(WagtailPageTestCase):
    TEMPLATE = Template('{% load topic_tags %} {% topics test_topics %}')

    def test_if_no_topics_template_should_be_empty(self):
        test_topics = TopicPage.objects.all()
        rendered = self.TEMPLATE.render(Context({'test_topics': test_topics}))

        self.assertEqual(' \n\n<ul class="topics">\n  \n</ul>\n', rendered)

    def test_correct_number_of_topics_render(self):
        for n in range(5):
            TopicPage.objects.create(path='/topic{0}'.format(n), depth=1, title='topic{0}'.format(n), slug='topic{0}'.format(n), archive=0, live=True)
        test_topics = TopicPage.objects.all()
        rendered = self.TEMPLATE.render(Context({'test_topics': test_topics}))

        self.assertIn('topic4', rendered)
        self.assertNotIn('topic5', rendered)

    def test_topics_not_live_should_not_render(self):
        TopicPage.objects.create(path='/topic1', depth=1, title='topic1', slug='topic1', archive=1, live=False)
        test_topics = TopicPage.objects.all()

        rendered = self.TEMPLATE.render(Context({'test_topics': test_topics}))
        self.assertNotIn('topic1', rendered)

    def test_topics_archived_should_render(self):
        TopicPage.objects.create(path='/topic1', depth=1, title='topic1', slug='topic1', archive=1, live=True)
        test_topics = TopicPage.objects.all()

        rendered = self.TEMPLATE.render(Context({'test_topics': test_topics}))
        self.assertIn('topic1', rendered)


# class TopicPageViewSetTests(WagtailPageTestCase):
#     fixtures = ['topics.json']
#     limit = 40
#
#     def get_api_url(self):
#         return f'/api/topics/?limit={self.limit}&offset=0&fields=title,url'
#
#     def verify_res_items(self, responseItems, expectedItems):
#         for i in range(len(expectedItems)):
#             self.assertEqual(responseItems[i]['title'], expectedItems[i]['title'])
#             self.assertEqual(responseItems[i]['url'], expectedItems[i]['url'])
#
#     def test_query_returns_200(self):
#         res = self.client.get(self.get_api_url())
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 31)
#         self.assertEqual(len(resJson['items']), 31)
#
#         self.verify_res_items(resJson['items'], [{
#             'title': 'Africa',
#             'url': '/topics/africa/'
#         }, {
#             'title': 'Artificial Intelligence',
#             'url': '/topics/artificial-intelligence/',
#         }, {
#             'title': 'Big Data',
#             'url': '/topics/big-data/',
#         }, {
#             'title': 'Central Banking',
#             'url': '/topics/central-banking/',
#         }, {
#             'title': 'China',
#             'url': '/topics/china/',
#         }, {
#             'title': 'Cybersecurity',
#             'url': '/topics/cybersecurity/',
#         }, {
#             'title': 'Democracy',
#             'url': '/topics/democracy/',
#         }, {
#             'title': 'Digital Currency',
#             'url': '/topics/digital-currency/',
#         }, {
#             'title': 'Emerging Technology',
#             'url': '/topics/emerging-technology/',
#         }, {
#             'title': 'Financial Systems',
#             'url': '/topics/financial-systems/',
#         }, {
#             'title': 'Future of Work',
#             'url': '/topics/future-of-work/',
#         }, {
#             'title': 'G20/G7',
#             'url': '/topics/g20-g7/',
#         }, {
#             'title': 'Gender',
#             'url': '/topics/gender/',
#         }, {
#             'title': 'IMF',
#             'url': '/topics/imf/',
#         }, {
#             'title': 'India',
#             'url': '/topics/india/',
#         }, {
#             'title': 'Innovation',
#             'url': '/topics/innovation/',
#         }, {
#             'title': 'Innovation Economy',
#             'url': '/topics/innovation-economy/',
#         }, {
#             'title': 'Intellectual Property',
#             'url': '/topics/intellectual-property/',
#         }, {
#             'title': 'Internet Governance',
#             'url': '/topics/internet-governance/',
#         }, {
#             'title': 'Investor State Arbitration',
#             'url': '/topics/investor-state-arbitration/',
#         }, {
#             'title': 'Monetary Policy',
#             'url': '/topics/monetary-policy/',
#         }, {
#             'title': 'NAFTA/CUSMA',
#             'url': '/topics/nafta-cusma/',
#         }, {
#             'title': 'Patents',
#             'url': '/topics/patents/',
#         }, {
#             'title': 'Platform Governance',
#             'url': '/topics/platform-governance/',
#         }, {
#             'title': 'Productivity',
#             'url': '/topics/productivity/',
#         }, {
#             'title': 'Sovereign Debt',
#             'url': '/topics/sovereign-debt/',
#         }, {
#             'title': 'Standards',
#             'url': '/topics/standards/',
#         }, {
#             'title': 'Surveillance & Privacy',
#             'url': '/topics/surveillance-privacy/',
#         }, {
#             'title': 'Systemic Risk',
#             'url': '/topics/systemic-risk/',
#         }, {
#             'title': 'Trade',
#             'url': '/topics/trade/',
#         }, {
#             'title': 'WTO',
#             'url': '/topics/wto/',
#         }])
