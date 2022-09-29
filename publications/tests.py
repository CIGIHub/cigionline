from home.models import HomePage
from wagtail.test.utils import WagtailPageTests

from .models import (
    PublicationListPage,
    PublicationPage,
    PublicationSeriesListPage,
    PublicationSeriesPage,
    PublicationTypePage,
)


class PublicationListPageTests(WagtailPageTests):
    def test_publicationlistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            PublicationListPage,
            {HomePage},
        )

    def test_publicationlistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            PublicationListPage,
            {PublicationPage, PublicationTypePage},
        )


class PublicationPageTests(WagtailPageTests):
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


class PublicationSeriesListPageTests(WagtailPageTests):
    def test_publicationserieslistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            PublicationSeriesListPage,
            {HomePage},
        )

    def test_publicationserieslistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            PublicationSeriesListPage,
            {PublicationSeriesPage},
        )


class PublicationSeriesPageTests(WagtailPageTests):
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


class PublicationTypePageTests(WagtailPageTests):
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


# class PublicationPageViewSetTests(WagtailPageTests):
#     fixtures = ['publications_search_table.json']
#     limit = 24
#
#     def setUp(self):
#         home_page = HomePage.objects.get()
#         home_page.numchild = 2
#         home_page.save()
#
#     def get_api_url(self, page):
#         offset = (page - 1) * self.limit
#         return f'/api/publications/?limit={self.limit}&offset={offset}&fields=authors,pdf_downloads,publishing_date,title,topics(title,url),url'
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
#                 self.assertTrue(any(topic['title'] == topicTitle for topic in responseItems[i]['topics']), f'Could not find topic:{topicTitle} for publication:{expectedItems[i]["title"]}')
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
#             'title': 'Test Publication 30',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-30/',
#         }, {
#             'publishing_date': '2020-12-22T08:00:00-05:00',
#             'title': 'Test Publication 29',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-29/',
#         }, {
#             'publishing_date': '2020-12-11T08:00:00-05:00',
#             'title': 'Test Publication 28',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-28/',
#         }, {
#             'publishing_date': '2020-12-09T08:00:00-05:00',
#             'title': 'Test Publication 27',
#             'topics': ['Test Topic 2', 'Test Topic 3'],
#             'url': '/publications/publication-27/',
#         }, {
#             'publishing_date': '2020-12-02T08:00:00-05:00',
#             'title': 'Test Publication 26',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-26/',
#         }, {
#             'publishing_date': '2020-11-30T08:00:00-05:00',
#             'title': 'Test Publication 25',
#             'topics': ['Test Topic 1', 'Test Topic 2'],
#             'url': '/publications/publication-25/',
#         }, {
#             'publishing_date': '2020-10-12T08:00:00-04:00',
#             'title': 'Test Publication 24 - Big Tech',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-24/',
#         }, {
#             'publishing_date': '2020-10-07T08:00:00-04:00',
#             'title': 'Test Publication 23',
#             'topics': ['Test Topic 2', 'Test Topic 3'],
#             'url': '/publications/publication-23/',
#         }, {
#             'publishing_date': '2020-09-23T08:00:00-04:00',
#             'title': 'Test Publication 22',
#             'topics': ['Test Topic 2'],
#             'url': '/publications/publication-22/',
#         }, {
#             'publishing_date': '2020-09-10T08:00:00-04:00',
#             'title': 'Test Publication 21',
#             'topics': ['Test Topic 2'],
#             'url': '/publications/publication-21/',
#         }, {
#             'publishing_date': '2020-08-28T08:00:00-04:00',
#             'title': 'Test Publication 20',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-20/',
#         }, {
#             'publishing_date': '2020-07-31T08:00:00-04:00',
#             'title': 'Test Publication 19',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-19/',
#         }, {
#             'publishing_date': '2020-07-29T08:00:00-04:00',
#             'title': 'Test Publication 18',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-18/',
#         }, {
#             'publishing_date': '2020-07-27T08:00:00-04:00',
#             'title': 'Test Publication 17 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-17/',
#         }, {
#             'publishing_date': '2020-06-23T08:00:00-04:00',
#             'title': 'Test Publication 16',
#             'topics': ['Test Topic 2'],
#             'url': '/publications/publication-16/',
#         }, {
#             'publishing_date': '2020-06-19T08:00:00-04:00',
#             'title': 'Test Publication 15',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-15/',
#         }, {
#             'publishing_date': '2020-06-18T08:00:00-04:00',
#             'title': 'Test Publication 14',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-14/',
#         }, {
#             'publishing_date': '2020-06-05T08:00:00-04:00',
#             'title': 'Test Publication 13',
#             'topics': ['Test Topic 2'],
#             'url': '/publications/publication-13/',
#         }, {
#             'publishing_date': '2020-05-12T08:00:00-04:00',
#             'title': 'Test Publication 12',
#             'topics': ['Test Topic 2'],
#             'url': '/publications/publication-12/',
#         }, {
#             'publishing_date': '2020-05-01T08:00:00-04:00',
#             'title': 'Test Publication 11',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-11/',
#         }, {
#             'publishing_date': '2020-04-17T08:00:00-04:00',
#             'title': 'Test Publication 10',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-10/',
#         }, {
#             'publishing_date': '2020-04-03T08:00:00-04:00',
#             'title': 'Test Publication 9',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-9/',
#         }, {
#             'publishing_date': '2020-03-25T08:00:00-04:00',
#             'title': 'Test Publication 8',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-8/',
#         }, {
#             'publishing_date': '2020-03-24T08:00:00-04:00',
#             'title': 'Test Publication 7',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-7/',
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
#             'publishing_date': '2020-03-20T08:00:00-04:00',
#             'title': 'Test Publication 6',
#             'topics': ['Test Topic 2'],
#             'url': '/publications/publication-6/',
#         }, {
#             'publishing_date': '2020-02-28T08:00:00-05:00',
#             'title': 'Test Publication 5',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-5/',
#         }, {
#             'publishing_date': '2020-01-29T08:00:00-05:00',
#             'title': 'Test Publication 4',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-4/',
#         }, {
#             'publishing_date': '2020-01-22T08:00:00-05:00',
#             'title': 'Test Publication 3',
#             'topics': ['Test Topic 2'],
#             'url': '/publications/publication-3/',
#         }, {
#             'publishing_date': '2020-01-16T08:00:00-05:00',
#             'title': 'Test Publication 2 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-2/',
#         }, {
#             'publishing_date': '2020-01-15T08:00:00-05:00',
#             'title': 'Test Publication 1',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-1/',
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
#         self.assertEqual(resJson['meta']['total_count'], 4)
#         self.assertEqual(len(resJson['items']), 4)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-10-12T08:00:00-04:00',
#             'title': 'Test Publication 24 - Big Tech',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-24/',
#         }, {
#             'publishing_date': '2020-07-27T08:00:00-04:00',
#             'title': 'Test Publication 17 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-17/',
#         }, {
#             'publishing_date': '2020-01-16T08:00:00-05:00',
#             'title': 'Test Publication 2 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-2/',
#         }, {
#             'publishing_date': '2020-12-30T08:00:00-05:00',
#             'title': 'Test Publication 30',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-30/',
#         }])
#
#     def test_filter_topic_1_returns_200(self):
#         topic1 = TopicPage.objects.get(title='Test Topic 1')
#         res = self.client.get(f'{self.get_api_url(1)}&topics={topic1.id}')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 14)
#         self.assertEqual(len(resJson['items']), 14)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-12-30T08:00:00-05:00',
#             'title': 'Test Publication 30',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-30/',
#         }, {
#             'publishing_date': '2020-12-22T08:00:00-05:00',
#             'title': 'Test Publication 29',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-29/',
#         }, {
#             'publishing_date': '2020-12-11T08:00:00-05:00',
#             'title': 'Test Publication 28',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-28/',
#         }, {
#             'publishing_date': '2020-12-02T08:00:00-05:00',
#             'title': 'Test Publication 26',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-26/',
#         }, {
#             'publishing_date': '2020-11-30T08:00:00-05:00',
#             'title': 'Test Publication 25',
#             'topics': ['Test Topic 1', 'Test Topic 2'],
#             'url': '/publications/publication-25/',
#         }, {
#             'publishing_date': '2020-08-28T08:00:00-04:00',
#             'title': 'Test Publication 20',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-20/',
#         }, {
#             'publishing_date': '2020-07-31T08:00:00-04:00',
#             'title': 'Test Publication 19',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-19/',
#         }, {
#             'publishing_date': '2020-07-29T08:00:00-04:00',
#             'title': 'Test Publication 18',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-18/',
#         }, {
#             'publishing_date': '2020-07-27T08:00:00-04:00',
#             'title': 'Test Publication 17 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-17/',
#         }, {
#             'publishing_date': '2020-06-19T08:00:00-04:00',
#             'title': 'Test Publication 15',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-15/',
#         }, {
#             'publishing_date': '2020-04-03T08:00:00-04:00',
#             'title': 'Test Publication 9',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-9/',
#         }, {
#             'publishing_date': '2020-01-29T08:00:00-05:00',
#             'title': 'Test Publication 4',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-4/',
#         }, {
#             'publishing_date': '2020-01-16T08:00:00-05:00',
#             'title': 'Test Publication 2 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-2/',
#         }, {
#             'publishing_date': '2020-01-15T08:00:00-05:00',
#             'title': 'Test Publication 1',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-1/',
#         }])
#
#     def test_filter_topic_2_returns_200(self):
#         topic2 = TopicPage.objects.get(title='Test Topic 2')
#         res = self.client.get(f'{self.get_api_url(1)}&topics={topic2.id}')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 10)
#         self.assertEqual(len(resJson['items']), 10)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-12-09T08:00:00-05:00',
#             'title': 'Test Publication 27',
#             'topics': ['Test Topic 2', 'Test Topic 3'],
#             'url': '/publications/publication-27/',
#         }, {
#             'publishing_date': '2020-11-30T08:00:00-05:00',
#             'title': 'Test Publication 25',
#             'topics': ['Test Topic 1', 'Test Topic 2'],
#             'url': '/publications/publication-25/',
#         }, {
#             'publishing_date': '2020-10-07T08:00:00-04:00',
#             'title': 'Test Publication 23',
#             'topics': ['Test Topic 2', 'Test Topic 3'],
#             'url': '/publications/publication-23/',
#         }, {
#             'publishing_date': '2020-09-23T08:00:00-04:00',
#             'title': 'Test Publication 22',
#             'topics': ['Test Topic 2'],
#             'url': '/publications/publication-22/',
#         }, {
#             'publishing_date': '2020-09-10T08:00:00-04:00',
#             'title': 'Test Publication 21',
#             'topics': ['Test Topic 2'],
#             'url': '/publications/publication-21/',
#         }, {
#             'publishing_date': '2020-06-23T08:00:00-04:00',
#             'title': 'Test Publication 16',
#             'topics': ['Test Topic 2'],
#             'url': '/publications/publication-16/',
#         }, {
#             'publishing_date': '2020-06-05T08:00:00-04:00',
#             'title': 'Test Publication 13',
#             'topics': ['Test Topic 2'],
#             'url': '/publications/publication-13/',
#         }, {
#             'publishing_date': '2020-05-12T08:00:00-04:00',
#             'title': 'Test Publication 12',
#             'topics': ['Test Topic 2'],
#             'url': '/publications/publication-12/',
#         }, {
#             'publishing_date': '2020-03-20T08:00:00-04:00',
#             'title': 'Test Publication 6',
#             'topics': ['Test Topic 2'],
#             'url': '/publications/publication-6/',
#         }, {
#             'publishing_date': '2020-01-22T08:00:00-05:00',
#             'title': 'Test Publication 3',
#             'topics': ['Test Topic 2'],
#             'url': '/publications/publication-3/',
#         }])
#
#     def test_filter_topic_3_returns_200(self):
#         topic3 = TopicPage.objects.get(title='Test Topic 3')
#         res = self.client.get(f'{self.get_api_url(1)}&topics={topic3.id}')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 9)
#         self.assertTrue(len(resJson['items']), 9)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-12-09T08:00:00-05:00',
#             'title': 'Test Publication 27',
#             'topics': ['Test Topic 2', 'Test Topic 3'],
#             'url': '/publications/publication-27/',
#         }, {
#             'publishing_date': '2020-10-12T08:00:00-04:00',
#             'title': 'Test Publication 24 - Big Tech',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-24/',
#         }, {
#             'publishing_date': '2020-10-07T08:00:00-04:00',
#             'title': 'Test Publication 23',
#             'topics': ['Test Topic 2', 'Test Topic 3'],
#             'url': '/publications/publication-23/',
#         }, {
#             'publishing_date': '2020-06-18T08:00:00-04:00',
#             'title': 'Test Publication 14',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-14/',
#         }, {
#             'publishing_date': '2020-05-01T08:00:00-04:00',
#             'title': 'Test Publication 11',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-11/',
#         }, {
#             'publishing_date': '2020-04-17T08:00:00-04:00',
#             'title': 'Test Publication 10',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-10/',
#         }, {
#             'publishing_date': '2020-03-25T08:00:00-04:00',
#             'title': 'Test Publication 8',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-8/',
#         }, {
#             'publishing_date': '2020-03-24T08:00:00-04:00',
#             'title': 'Test Publication 7',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-7/',
#         }, {
#             'publishing_date': '2020-02-28T08:00:00-05:00',
#             'title': 'Test Publication 5',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-5/',
#         }])
#
#     def test_filter_publication_type_books_returns_200(self):
#         res = self.client.get(f'{self.get_api_url(1)}&publication_type=42')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 4)
#         self.assertEqual(len(resJson['items']), 4)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-12-11T08:00:00-05:00',
#             'title': 'Test Publication 28',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-28/',
#         }, {
#             'publishing_date': '2020-06-19T08:00:00-04:00',
#             'title': 'Test Publication 15',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-15/',
#         }, {
#             'publishing_date': '2020-06-18T08:00:00-04:00',
#             'title': 'Test Publication 14',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-14/',
#         }, {
#             'publishing_date': '2020-01-22T08:00:00-05:00',
#             'title': 'Test Publication 3',
#             'topics': ['Test Topic 2'],
#             'url': '/publications/publication-3/',
#         }])
#
#     def test_filter_publication_type_cigi_papers_returns_200(self):
#         res = self.client.get(f'{self.get_api_url(1)}&publication_type=41')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 13)
#         self.assertEqual(len(resJson['items']), 13)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-12-30T08:00:00-05:00',
#             'title': 'Test Publication 30',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-30/',
#         }, {
#             'publishing_date': '2020-12-09T08:00:00-05:00',
#             'title': 'Test Publication 27',
#             'topics': ['Test Topic 2', 'Test Topic 3'],
#             'url': '/publications/publication-27/',
#         }, {
#             'publishing_date': '2020-12-02T08:00:00-05:00',
#             'title': 'Test Publication 26',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-26/',
#         }, {
#             'publishing_date': '2020-11-30T08:00:00-05:00',
#             'title': 'Test Publication 25',
#             'topics': ['Test Topic 1', 'Test Topic 2'],
#             'url': '/publications/publication-25/',
#         }, {
#             'publishing_date': '2020-10-12T08:00:00-04:00',
#             'title': 'Test Publication 24 - Big Tech',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-24/',
#         }, {
#             'publishing_date': '2020-10-07T08:00:00-04:00',
#             'title': 'Test Publication 23',
#             'topics': ['Test Topic 2', 'Test Topic 3'],
#             'url': '/publications/publication-23/',
#         }, {
#             'publishing_date': '2020-08-28T08:00:00-04:00',
#             'title': 'Test Publication 20',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-20/',
#         }, {
#             'publishing_date': '2020-07-27T08:00:00-04:00',
#             'title': 'Test Publication 17 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-17/',
#         }, {
#             'publishing_date': '2020-06-23T08:00:00-04:00',
#             'title': 'Test Publication 16',
#             'topics': ['Test Topic 2'],
#             'url': '/publications/publication-16/',
#         }, {
#             'publishing_date': '2020-06-05T08:00:00-04:00',
#             'title': 'Test Publication 13',
#             'topics': ['Test Topic 2'],
#             'url': '/publications/publication-13/',
#         }, {
#             'publishing_date': '2020-03-25T08:00:00-04:00',
#             'title': 'Test Publication 8',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-8/',
#         }, {
#             'publishing_date': '2020-01-16T08:00:00-05:00',
#             'title': 'Test Publication 2 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-2/',
#         }, {
#             'publishing_date': '2020-01-15T08:00:00-05:00',
#             'title': 'Test Publication 1',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-1/',
#         }])
#
#     def test_filter_publication_type_conference_reports_returns_200(self):
#         res = self.client.get(f'{self.get_api_url(1)}&publication_type=43')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 1)
#         self.assertEqual(len(resJson['items']), 1)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-01-29T08:00:00-05:00',
#             'title': 'Test Publication 4',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-4/',
#         }])
#
#     def test_filter_publication_type_essay_series_returns_200(self):
#         res = self.client.get(f'{self.get_api_url(1)}&publication_type=47')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 2)
#         self.assertEqual(len(resJson['items']), 2)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-09-10T08:00:00-04:00',
#             'title': 'Test Publication 21',
#             'topics': ['Test Topic 2'],
#             'url': '/publications/publication-21/',
#         }, {
#             'publishing_date': '2020-04-03T08:00:00-04:00',
#             'title': 'Test Publication 9',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-9/',
#         }])
#
#     def test_filter_publication_type_policy_briefs_returns_200(self):
#         res = self.client.get(f'{self.get_api_url(1)}&publication_type=48')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 2)
#         self.assertEqual(len(resJson['items']), 2)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-07-31T08:00:00-04:00',
#             'title': 'Test Publication 19',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-19/',
#         }, {
#             'publishing_date': '2020-04-17T08:00:00-04:00',
#             'title': 'Test Publication 10',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-10/',
#         }])
#
#     def test_filter_publication_type_policy_memos_returns_200(self):
#         res = self.client.get(f'{self.get_api_url(1)}&publication_type=46')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 2)
#         self.assertEqual(len(resJson['items']), 2)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-09-23T08:00:00-04:00',
#             'title': 'Test Publication 22',
#             'topics': ['Test Topic 2'],
#             'url': '/publications/publication-22/',
#         }, {
#             'publishing_date': '2020-03-24T08:00:00-04:00',
#             'title': 'Test Publication 7',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-7/',
#         }])
#
#     def test_filter_publication_type_special_reports_returns_200(self):
#         res = self.client.get(f'{self.get_api_url(1)}&publication_type=44')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 4)
#         self.assertEqual(len(resJson['items']), 4)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-12-22T08:00:00-05:00',
#             'title': 'Test Publication 29',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-29/',
#         }, {
#             'publishing_date': '2020-07-29T08:00:00-04:00',
#             'title': 'Test Publication 18',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-18/',
#         }, {
#             'publishing_date': '2020-05-12T08:00:00-04:00',
#             'title': 'Test Publication 12',
#             'topics': ['Test Topic 2'],
#             'url': '/publications/publication-12/',
#         }, {
#             'publishing_date': '2020-02-28T08:00:00-05:00',
#             'title': 'Test Publication 5',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-5/',
#         }])
#
#     def test_search_and_filter_topics_returns_200(self):
#         topic1 = TopicPage.objects.get(title='Test Topic 1')
#         res = self.client.get(f'{self.get_api_url(1)}&search=big+tech&topics={topic1.id}')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 3)
#         self.assertEqual(len(resJson['items']), 3)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-07-27T08:00:00-04:00',
#             'title': 'Test Publication 17 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-17/',
#         }, {
#             'publishing_date': '2020-01-16T08:00:00-05:00',
#             'title': 'Test Publication 2 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-2/',
#         }, {
#             'publishing_date': '2020-12-30T08:00:00-05:00',
#             'title': 'Test Publication 30',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-30/',
#         }])
#
#     def test_search_and_filter_publication_type_cigi_papers_returns_200(self):
#         res = self.client.get(f'{self.get_api_url(1)}&search=big+tech&publication_type=41')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 4)
#         self.assertEqual(len(resJson['items']), 4)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-10-12T08:00:00-04:00',
#             'title': 'Test Publication 24 - Big Tech',
#             'topics': ['Test Topic 3'],
#             'url': '/publications/publication-24/',
#         }, {
#             'publishing_date': '2020-07-27T08:00:00-04:00',
#             'title': 'Test Publication 17 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-17/',
#         }, {
#             'publishing_date': '2020-01-16T08:00:00-05:00',
#             'title': 'Test Publication 2 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-2/',
#         }, {
#             'publishing_date': '2020-12-30T08:00:00-05:00',
#             'title': 'Test Publication 30',
#             'topics': ['Test Topic 1'],
#             'url': '/publications/publication-30/',
#         }])
#
#     def test_search_and_filter_publication_type_essay_series_returns_200(self):
#         res = self.client.get(f'{self.get_api_url(1)}&search=big+tech&publication_type=47')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 0)
#         self.assertEqual(len(resJson['items']), 0)
