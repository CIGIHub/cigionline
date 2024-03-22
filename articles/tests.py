from home.models import HomePage
from wagtail.test.utils import WagtailPageTestCase

from .models import (
    ArticleLandingPage,
    ArticleListPage,
    ArticlePage,
    ArticleSeriesListPage,
    ArticleSeriesPage,
    ArticleTypePage,
    MediaLandingPage,
    OpinionSeriesListPage,
)


class ArticleLandingPageTests(WagtailPageTestCase):
    def test_articlelandingpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            ArticleLandingPage,
            {HomePage},
        )

    def test_articlelandingpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            ArticleLandingPage,
            {OpinionSeriesListPage},
        )


class ArticleListPageTests(WagtailPageTestCase):
    def test_articlelistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            ArticleListPage,
            {HomePage},
        )

    def test_articlelistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            ArticleListPage,
            {ArticlePage, ArticleTypePage},
        )


class ArticlePageTests(WagtailPageTestCase):
    def test_articlepage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            ArticlePage,
            {ArticleListPage},
        )

    def test_articlepage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            ArticlePage,
            {},
        )


class ArticleSeriesListPageTests(WagtailPageTestCase):
    def test_articleserieslistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            ArticleSeriesListPage,
            {HomePage},
        )

    def test_articleserieslistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            ArticleSeriesListPage,
            {},
        )


class ArticleSeriesPageTests(WagtailPageTestCase):
    def test_articleseriespage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            ArticleSeriesPage,
            {HomePage},
        )

    def test_articleseriespage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            ArticleSeriesPage,
            {},
        )


class MediaLandingPageTests(WagtailPageTestCase):
    def test_articlelandingpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            MediaLandingPage,
            {HomePage},
        )

    def test_articlelandingpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            MediaLandingPage,
            {},
        )


class ArticleTypePageTests(WagtailPageTestCase):
    def test_articletypepage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            ArticleTypePage,
            {ArticleListPage},
        )

    def test_articletypepage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            ArticleTypePage,
            {},
        )


# class OpinionPageViewSetTests(WagtailPageTestCase):
#     fixtures = ['opinions_search_table.json']
#     limit = 24
#
#     def get_api_url(self, page):
#         offset = (page - 1) * self.limit
#         return f'/api/opinions/?limit={self.limit}&offset={offset}&fields=authors,publishing_date,title,topics(title,url),url'
#
#     def verify_res_items(self, responseItems, expectedItems):
#         for i in range(len(expectedItems)):
#             self.assertEqual(responseItems[i]['title'], expectedItems[i]['title'])
#             self.assertEqual(responseItems[i]['url'], expectedItems[i]['url'])
#             self.assertEqual(responseItems[i]['publishing_date'], expectedItems[i]['publishing_date'])
#
#             self.assertEqual(len(responseItems[i]['topics']), len(expectedItems[i]['topics']), f'Length of topics: {expectedItems[i]["title"]}')
#             # Verify that the expected topic titles were returned in the response
#             for topicTitle in expectedItems[i]['topics']:
#                 self.assertTrue(any(topic['title'] == topicTitle for topic in responseItems[i]['topics']), f'Could not find topic:{topicTitle} for opinion:{expectedItems[i]["title"]}')
#
#     def test_page_1_query_returns_200(self):
#         res = self.client.get(self.get_api_url(1))
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 30)
#         self.assertEqual(len(resJson['items']), 24)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-12-30T08:00:00-05:00',
#             'title': 'Test Article 30',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-30/',
#         }, {
#             'publishing_date': '2020-12-23T08:00:00-05:00',
#             'title': 'Test Article 29',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-29/',
#         }, {
#             'publishing_date': '2020-12-09T08:00:00-05:00',
#             'title': 'Test Article 28 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-28/',
#         }, {
#             'publishing_date': '2020-12-04T08:00:00-05:00',
#             'title': 'Test Article 27',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-27/',
#         }, {
#             'publishing_date': '2020-12-03T08:00:00-05:00',
#             'title': 'Test Article 26',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-26/',
#         }, {
#             'publishing_date': '2020-11-23T08:00:00-05:00',
#             'title': 'Test Article 25',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-25/',
#         }, {
#             'publishing_date': '2020-11-20T08:00:00-05:00',
#             'title': 'Test Article 24',
#             'topics': ['Test Topic 2', 'Test Topic 3'],
#             'url': '/articles/article-24/',
#         }, {
#             'publishing_date': '2020-11-06T08:00:00-05:00',
#             'title': 'Test Article 23',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-23/',
#         }, {
#             'publishing_date': '2020-10-15T08:00:00-04:00',
#             'title': 'Test Article 22',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-22/',
#         }, {
#             'publishing_date': '2020-10-07T08:00:00-04:00',
#             'title': 'Test Article 21',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-21/',
#         }, {
#             'publishing_date': '2020-10-06T08:00:00-04:00',
#             'title': 'Test Article 20',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-20/',
#         }, {
#             'publishing_date': '2020-10-02T08:00:00-04:00',
#             'title': 'Test Article 19',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-19/',
#         }, {
#             'publishing_date': '2020-09-09T08:00:00-04:00',
#             'title': 'Test Article 18',
#             'topics': ['Test Topic 2'],
#             'url': '/articles/article-18/',
#         }, {
#             'publishing_date': '2020-09-03T08:00:00-04:00',
#             'title': 'Test Article 17',
#             'topics': ['Test Topic 1', 'Test Topic 2'],
#             'url': '/articles/article-17/',
#         }, {
#             'publishing_date': '2020-08-19T08:00:00-04:00',
#             'title': 'Test Article 16',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-16/',
#         }, {
#             'publishing_date': '2020-08-14T08:00:00-04:00',
#             'title': 'Test Article 15',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-15/',
#         }, {
#             'publishing_date': '2020-07-21T08:00:00-04:00',
#             'title': 'Test Article 14',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-14/',
#         }, {
#             'publishing_date': '2020-07-13T08:00:00-04:00',
#             'title': 'Test Article 13',
#             'topics': ['Test Topic 2'],
#             'url': '/articles/article-13/',
#         }, {
#             'publishing_date': '2020-07-09T08:00:00-04:00',
#             'title': 'Test Article 12',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-12/',
#         }, {
#             'publishing_date': '2020-06-03T08:00:00-04:00',
#             'title': 'Test Article 11',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-11/',
#         }, {
#             'publishing_date': '2020-06-02T08:00:00-04:00',
#             'title': 'Test Article 10',
#             'topics': ['Test Topic 2'],
#             'url': '/articles/article-10/',
#         }, {
#             'publishing_date': '2020-05-11T08:00:00-04:00',
#             'title': 'Test Article 9',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-9/',
#         }, {
#             'publishing_date': '2020-05-07T08:00:00-04:00',
#             'title': 'Test Article 8',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-8/',
#         }, {
#             'publishing_date': '2020-03-17T08:00:00-04:00',
#             'title': 'Test Article 7',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-7/',
#         }])
#
#     def test_page_2_query_returns_200(self):
#         res = self.client.get(self.get_api_url(2))
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 30)
#         self.assertEqual(len(resJson['items']), 6)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-03-09T08:00:00-04:00',
#             'title': 'Test Article 6',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-6/',
#         }, {
#             'publishing_date': '2020-03-06T08:00:00-05:00',
#             'title': 'Test Article 5',
#             'topics': ['Test Topic 2'],
#             'url': '/articles/article-5/',
#         }, {
#             'publishing_date': '2020-02-18T08:00:00-05:00',
#             'title': 'Test Article 4',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-4/',
#         }, {
#             'publishing_date': '2020-01-16T08:00:00-05:00',
#             'title': 'Test Article 3',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-3/',
#         }, {
#             'publishing_date': '2020-01-09T08:00:00-05:00',
#             'title': 'Test Article 2 - Big Tech',
#             'topics': ['Test Topic 2'],
#             'url': '/articles/article-2/',
#         }, {
#             'publishing_date': '2020-01-06T08:00:00-05:00',
#             'title': 'Test Article 1',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-1/',
#         }])
#
#     def test_page_3_returns_200(self):
#         res = self.client.get(self.get_api_url(3))
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 30)
#         self.assertEqual(len(resJson['items']), 0)
#
#     def test_search_query_returns_200(self):
#         res = self.client.get(f'{self.get_api_url(1)}&search=big+tech')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 3)
#         self.assertEqual(len(resJson['items']), 3)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-12-09T08:00:00-05:00',
#             'title': 'Test Article 28 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-28/',
#         }, {
#             'publishing_date': '2020-01-09T08:00:00-05:00',
#             'title': 'Test Article 2 - Big Tech',
#             'topics': ['Test Topic 2'],
#             'url': '/articles/article-2/',
#         }, {
#             'publishing_date': '2020-07-09T08:00:00-04:00',
#             'title': 'Test Article 12',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-12/',
#         }])
#
#     def test_filter_topic_1_returns_200(self):
#         topic1 = TopicPage.objects.get(title='Test Topic 1')
#         res = self.client.get(f'{self.get_api_url(1)}&topics={topic1.id}')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 10)
#         self.assertEqual(len(resJson['items']), 10)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-12-09T08:00:00-05:00',
#             'title': 'Test Article 28 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-28/',
#         }, {
#             'publishing_date': '2020-12-04T08:00:00-05:00',
#             'title': 'Test Article 27',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-27/',
#         }, {
#             'publishing_date': '2020-10-06T08:00:00-04:00',
#             'title': 'Test Article 20',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-20/',
#         }, {
#             'publishing_date': '2020-10-02T08:00:00-04:00',
#             'title': 'Test Article 19',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-19/',
#         }, {
#             'publishing_date': '2020-09-03T08:00:00-04:00',
#             'title': 'Test Article 17',
#             'topics': ['Test Topic 1', 'Test Topic 2'],
#             'url': '/articles/article-17/',
#         }, {
#             'publishing_date': '2020-08-19T08:00:00-04:00',
#             'title': 'Test Article 16',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-16/',
#         }, {
#             'publishing_date': '2020-07-09T08:00:00-04:00',
#             'title': 'Test Article 12',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-12/',
#         }, {
#             'publishing_date': '2020-06-03T08:00:00-04:00',
#             'title': 'Test Article 11',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-11/',
#         }, {
#             'publishing_date': '2020-03-09T08:00:00-04:00',
#             'title': 'Test Article 6',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-6/',
#         }, {
#             'publishing_date': '2020-02-18T08:00:00-05:00',
#             'title': 'Test Article 4',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-4/',
#         }])
#
#     def test_filter_topic_2_returns_200(self):
#         topic2 = TopicPage.objects.get(title='Test Topic 2')
#         res = self.client.get(f'{self.get_api_url(1)}&topics={topic2.id}')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 7)
#         self.assertEqual(len(resJson['items']), 7)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-11-20T08:00:00-05:00',
#             'title': 'Test Article 24',
#             'topics': ['Test Topic 2', 'Test Topic 3'],
#             'url': '/articles/article-24/',
#         }, {
#             'publishing_date': '2020-09-09T08:00:00-04:00',
#             'title': 'Test Article 18',
#             'topics': ['Test Topic 2'],
#             'url': '/articles/article-18/',
#         }, {
#             'publishing_date': '2020-09-03T08:00:00-04:00',
#             'title': 'Test Article 17',
#             'topics': ['Test Topic 1', 'Test Topic 2'],
#             'url': '/articles/article-17/',
#         }, {
#             'publishing_date': '2020-07-13T08:00:00-04:00',
#             'title': 'Test Article 13',
#             'topics': ['Test Topic 2'],
#             'url': '/articles/article-13/',
#         }, {
#             'publishing_date': '2020-06-02T08:00:00-04:00',
#             'title': 'Test Article 10',
#             'topics': ['Test Topic 2'],
#             'url': '/articles/article-10/',
#         }, {
#             'publishing_date': '2020-03-06T08:00:00-05:00',
#             'title': 'Test Article 5',
#             'topics': ['Test Topic 2'],
#             'url': '/articles/article-5/',
#         }, {
#             'publishing_date': '2020-01-09T08:00:00-05:00',
#             'title': 'Test Article 2 - Big Tech',
#             'topics': ['Test Topic 2'],
#             'url': '/articles/article-2/',
#         }])
#
#     def test_filter_topic_3_returns_200(self):
#         topic3 = TopicPage.objects.get(title='Test Topic 3')
#         res = self.client.get(f'{self.get_api_url(1)}&topics={topic3.id}')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 15)
#         self.assertTrue(len(resJson['items']), 15)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-12-30T08:00:00-05:00',
#             'title': 'Test Article 30',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-30/',
#         }, {
#             'publishing_date': '2020-12-23T08:00:00-05:00',
#             'title': 'Test Article 29',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-29/',
#         }, {
#             'publishing_date': '2020-12-03T08:00:00-05:00',
#             'title': 'Test Article 26',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-26/',
#         }, {
#             'publishing_date': '2020-11-23T08:00:00-05:00',
#             'title': 'Test Article 25',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-25/',
#         }, {
#             'publishing_date': '2020-11-20T08:00:00-05:00',
#             'title': 'Test Article 24',
#             'topics': ['Test Topic 2', 'Test Topic 3'],
#             'url': '/articles/article-24/',
#         }, {
#             'publishing_date': '2020-11-06T08:00:00-05:00',
#             'title': 'Test Article 23',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-23/',
#         }, {
#             'publishing_date': '2020-10-15T08:00:00-04:00',
#             'title': 'Test Article 22',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-22/',
#         }, {
#             'publishing_date': '2020-10-07T08:00:00-04:00',
#             'title': 'Test Article 21',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-21/',
#         }, {
#             'publishing_date': '2020-08-14T08:00:00-04:00',
#             'title': 'Test Article 15',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-15/',
#         }, {
#             'publishing_date': '2020-07-21T08:00:00-04:00',
#             'title': 'Test Article 14',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-14/',
#         }, {
#             'publishing_date': '2020-05-11T08:00:00-04:00',
#             'title': 'Test Article 9',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-9/',
#         }, {
#             'publishing_date': '2020-05-07T08:00:00-04:00',
#             'title': 'Test Article 8',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-8/',
#         }, {
#             'publishing_date': '2020-03-17T08:00:00-04:00',
#             'title': 'Test Article 7',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-7/',
#         }, {
#             'publishing_date': '2020-01-16T08:00:00-05:00',
#             'title': 'Test Article 3',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-3/',
#         }, {
#             'publishing_date': '2020-01-06T08:00:00-05:00',
#             'title': 'Test Article 1',
#             'topics': ['Test Topic 3'],
#             'url': '/articles/article-1/',
#         }])
#
#     def test_search_and_filter_topics_returns_200(self):
#         topic1 = TopicPage.objects.get(title='Test Topic 1')
#         res = self.client.get(f'{self.get_api_url(1)}&search=big+tech&topics={topic1.id}')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 2)
#         self.assertEqual(len(resJson['items']), 2)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-12-09T08:00:00-05:00',
#             'title': 'Test Article 28 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-28/',
#         }, {
#             'publishing_date': '2020-07-09T08:00:00-04:00',
#             'title': 'Test Article 12',
#             'topics': ['Test Topic 1'],
#             'url': '/articles/article-12/',
#         }])
