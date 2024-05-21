from core.models import BasicPage
from wagtail.models import Page
from articles.models import ArticlePage, ArticleTypePage
from django.contrib.auth.models import User
from home.models import HomePage
from django.template import Context, Template
from django.utils.text import slugify
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import nested_form_data
from datetime import date

from .models import (
    ProjectListPage,
    ProjectPage,
    ResearchLandingPage,
    TopicListPage,
    TopicPage,
)


class ProjectListPageTests(WagtailPageTestCase):
    def test_projectlistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            ProjectListPage,
            {HomePage},
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


class HighlightedTopicsTests(WagtailPageTestCase):
    TEMPLATE = Template('{% load topic_tags %} {% highlighted_topics %}')

    def _tag_topic(self, topic_title, article_title):
        def create_page(page_model, page_title, parent_page_title):
            print('Creating page: {0}'.format(page_title))
            if not page_model.objects.filter(title=page_title).exists():
                if Page.objects.filter(title=parent_page_title).exists():
                    new_page = page_model(title=page_title)
                    parent_page = Page.objects.get(title=parent_page_title).specific
                    parent_page.add_child(instance=new_page)
                    print('Page created: {0}'.format(page_title))
                else:
                    print('Parent page does not exist: {0}'.format(parent_page_title))
            else:
                print('Page already exists: {0}'.format(page_title))

        create_page(Page, 'Articles', 'Home')
        create_page(ArticleTypePage, 'Test', 'Articles')

        if TopicPage.objects.filter(title=topic_title).exists():
            print('Topic exists: {0}'.format(topic_title))

        ArticlePage.objects.create(
            path='/{0}'.format(slugify(article_title)),
            depth=1,
            title=article_title,
            slug=slugify(article_title),
            publishing_date=date.today().strftime("%Y-%m-%d"),
            article_type=ArticleTypePage.objects.get(title='Test'),
            topics=[TopicPage.objects.get(title=topic_title)],
            live=True)

    def test_if_no_topics_template_should_be_empty(self):
        rendered = self.TEMPLATE.render(Context({}))

        self.assertEqual(' \n\n\n<ul class="highlighted-topics-list">\n  \n</ul>\n', rendered)

    def test_correct_number_of_topics_render(self):
        for n in range(5):
            TopicPage.objects.create(path='/topic{0}'.format(n), depth=1, title='topic{0}'.format(n), slug='topic{0}'.format(n), archive=0, live=True)
            self._tag_topic('topic{0}'.format(n), 'article{0}'.format(n))
        rendered = self.TEMPLATE.render(Context({}))

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
