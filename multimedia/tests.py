from home.models import HomePage
from wagtail.test.utils import WagtailPageTestCase

from .models import (
    MultimediaListPage,
    MultimediaPage,
    MultimediaSeriesListPage,
    MultimediaSeriesPage,
)


class MultimediaListPageTests(WagtailPageTestCase):
    def test_multimedialistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            MultimediaListPage,
            {HomePage},
        )

    def test_multimedialistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            MultimediaListPage,
            {MultimediaPage},
        )


class MultimediaPageTests(WagtailPageTestCase):
    def test_multimediapage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            MultimediaPage,
            {MultimediaListPage, MultimediaSeriesPage},
        )

    def test_multimediapage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            MultimediaPage,
            {},
        )


class MultimediaSeriesListPageTests(WagtailPageTestCase):
    def test_multimediaserieslistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            MultimediaSeriesListPage,
            {HomePage},
        )

    def test_multimediaserieslistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            MultimediaSeriesListPage,
            {MultimediaSeriesPage},
        )


class MultimediaSeriesPageTests(WagtailPageTestCase):
    def test_multimediaseriespage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            MultimediaSeriesPage,
            {HomePage, MultimediaSeriesListPage},
        )

    def test_multimediaseriespage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            MultimediaSeriesPage,
            {MultimediaPage},
        )


# class MultimediaPageViewSetTests(WagtailPageTestCase):
#     fixtures = ['multimedia_search_table.json']
#     limit = 18
#
#     def setUp(self):
#         home_page = HomePage.objects.get()
#         home_page.numchild = 2
#         home_page.save()
#
#     def get_api_url(self, page):
#         offset = (page - 1) * self.limit
#         return f'/api/multimedia/?limit={self.limit}&offset={offset}&fields=title,url,publishing_date,topics(title,url)'
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
#                 self.assertTrue(any(topic['title'] == topicTitle for topic in responseItems[i]['topics']), f'Could not find topic:{topicTitle} for multimedia:{expectedItems[i]["title"]}')
#
#     def test_page_1_query_returns_200(self):
#         res = self.client.get(self.get_api_url(1))
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 30)
#         self.assertEqual(len(resJson['items']), 18)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-12-25T08:00:00-05:00',
#             'title': 'Test Multimedia 30',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-30/',
#         }, {
#             'publishing_date': '2020-12-16T08:00:00-05:00',
#             'title': 'Test Multimedia 29',
#             'topics': ['Test Topic 2'],
#             'url': '/multimedia/multimedia-29/',
#         }, {
#             'publishing_date': '2020-12-11T08:00:00-05:00',
#             'title': 'Test Multimedia 28',
#             'topics': ['Test Topic 2'],
#             'url': '/multimedia/multimedia-28/',
#         }, {
#             'publishing_date': '2020-12-10T08:00:00-05:00',
#             'title': 'Test Multimedia 27',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-27/',
#         }, {
#             'publishing_date': '2020-12-07T08:00:00-05:00',
#             'title': 'Test Multimedia 26',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-26/',
#         }, {
#             'publishing_date': '2020-11-24T08:00:00-05:00',
#             'title': 'Test Multimedia 25',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-25/',
#         }, {
#             'publishing_date': '2020-11-05T08:00:00-05:00',
#             'title': 'Test Multimedia 24',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-24/',
#         }, {
#             'publishing_date': '2020-10-28T08:00:00-04:00',
#             'title': 'Test Multimedia 23',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-23/',
#         }, {
#             'publishing_date': '2020-10-27T08:00:00-04:00',
#             'title': 'Test Multimedia 22',
#             'topics': ['Test Topic 2'],
#             'url': '/multimedia/multimedia-22/',
#         }, {
#             'publishing_date': '2020-10-21T08:00:00-04:00',
#             'title': 'Test Multimedia 21',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-21/',
#         }, {
#             'publishing_date': '2020-10-15T08:00:00-04:00',
#             'title': 'Test Multimedia 20',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-20/',
#         }, {
#             'publishing_date': '2020-09-14T08:00:00-04:00',
#             'title': 'Test Multimedia 19',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-19/',
#         }, {
#             'publishing_date': '2020-09-03T08:00:00-04:00',
#             'title': 'Test Multimedia 18',
#             'topics': ['Test Topic 2'],
#             'url': '/multimedia/multimedia-18/',
#         }, {
#             'publishing_date': '2020-08-14T08:00:00-04:00',
#             'title': 'Test Multimedia 17',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-17/',
#         }, {
#             'publishing_date': '2020-08-12T08:00:00-04:00',
#             'title': 'Test Multimedia 16',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-16/',
#         }, {
#             'publishing_date': '2020-08-11T08:00:00-04:00',
#             'title': 'Test Multimedia 15',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-15/',
#         }, {
#             'publishing_date': '2020-08-06T08:00:00-04:00',
#             'title': 'Test Multimedia 14',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-14/',
#         }, {
#             'publishing_date': '2020-07-27T08:00:00-04:00',
#             'title': 'Test Multimedia 13',
#             'topics': ['Test Topic 2'],
#             'url': '/multimedia/multimedia-13/',
#         }])
#
#     def test_page_2_query_returns_200(self):
#         res = self.client.get(self.get_api_url(2))
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 30)
#         self.assertEqual(len(resJson['items']), 12)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-07-20T08:00:00-04:00',
#             'title': 'Test Multimedia 12 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-12/',
#         }, {
#             'publishing_date': '2020-07-06T08:00:00-04:00',
#             'title': 'Test Multimedia 11',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-11/',
#         }, {
#             'publishing_date': '2020-06-24T08:00:00-04:00',
#             'title': 'Test Multimedia 10',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-10/',
#         }, {
#             'publishing_date': '2020-06-19T08:00:00-04:00',
#             'title': 'Test Multimedia 9',
#             'topics': ['Test Topic 2'],
#             'url': '/multimedia/multimedia-9/',
#         }, {
#             'publishing_date': '2020-06-18T08:00:00-04:00',
#             'title': 'Test Multimedia 8',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-8/',
#         }, {
#             'publishing_date': '2020-06-16T08:00:00-04:00',
#             'title': 'Test Multimedia 7',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-7/',
#         }, {
#             'publishing_date': '2020-06-02T08:00:00-04:00',
#             'title': 'Test Multimedia 6',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-6/',
#         }, {
#             'publishing_date': '2020-05-07T08:00:00-04:00',
#             'title': 'Test Multimedia 5 - Big Tech',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-5/',
#         }, {
#             'publishing_date': '2020-04-24T08:00:00-04:00',
#             'title': 'Test Multimedia 4',
#             'topics': ['Test Topic 2', 'Test Topic 3'],
#             'url': '/multimedia/multimedia-4/',
#         }, {
#             'publishing_date': '2020-04-22T08:00:00-04:00',
#             'title': 'Test Multimedia 3',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-3/',
#         }, {
#             'publishing_date': '2020-04-20T08:00:00-04:00',
#             'title': 'Test Multimedia 2',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-2/',
#         }, {
#             'publishing_date': '2020-02-04T08:00:00-05:00',
#             'title': 'Test Multimedia 1',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-1/',
#         }])
#
#     def test_page_3_query_returns_200(self):
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
#             'publishing_date': '2020-07-20T08:00:00-04:00',
#             'title': 'Test Multimedia 12 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-12/',
#         }, {
#             'publishing_date': '2020-05-07T08:00:00-04:00',
#             'title': 'Test Multimedia 5 - Big Tech',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-5/',
#         }, {
#             'publishing_date': '2020-10-28T08:00:00-04:00',
#             'title': 'Test Multimedia 23',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-23/',
#         }])
#
#     def test_filter_topic_1_returns_200(self):
#         topic1 = TopicPage.objects.get(title='Test Topic 1')
#         res = self.client.get(f'{self.get_api_url(1)}&topics={topic1.id}')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 13)
#         self.assertEqual(len(resJson['items']), 13)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-12-25T08:00:00-05:00',
#             'title': 'Test Multimedia 30',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-30/',
#         }, {
#             'publishing_date': '2020-12-07T08:00:00-05:00',
#             'title': 'Test Multimedia 26',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-26/',
#         }, {
#             'publishing_date': '2020-11-24T08:00:00-05:00',
#             'title': 'Test Multimedia 25',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-25/',
#         }, {
#             'publishing_date': '2020-10-21T08:00:00-04:00',
#             'title': 'Test Multimedia 21',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-21/',
#         }, {
#             'publishing_date': '2020-09-14T08:00:00-04:00',
#             'title': 'Test Multimedia 19',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-19/',
#         }, {
#             'publishing_date': '2020-08-14T08:00:00-04:00',
#             'title': 'Test Multimedia 17',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-17/',
#         }, {
#             'publishing_date': '2020-08-12T08:00:00-04:00',
#             'title': 'Test Multimedia 16',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-16/',
#         }, {
#             'publishing_date': '2020-07-20T08:00:00-04:00',
#             'title': 'Test Multimedia 12 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-12/',
#         }, {
#             'publishing_date': '2020-06-18T08:00:00-04:00',
#             'title': 'Test Multimedia 8',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-8/',
#         }, {
#             'publishing_date': '2020-06-16T08:00:00-04:00',
#             'title': 'Test Multimedia 7',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-7/',
#         }, {
#             'publishing_date': '2020-06-02T08:00:00-04:00',
#             'title': 'Test Multimedia 6',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-6/',
#         }, {
#             'publishing_date': '2020-04-22T08:00:00-04:00',
#             'title': 'Test Multimedia 3',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-3/',
#         }, {
#             'publishing_date': '2020-02-04T08:00:00-05:00',
#             'title': 'Test Multimedia 1',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-1/',
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
#             'publishing_date': '2020-12-16T08:00:00-05:00',
#             'title': 'Test Multimedia 29',
#             'topics': ['Test Topic 2'],
#             'url': '/multimedia/multimedia-29/',
#         }, {
#             'publishing_date': '2020-12-11T08:00:00-05:00',
#             'title': 'Test Multimedia 28',
#             'topics': ['Test Topic 2'],
#             'url': '/multimedia/multimedia-28/',
#         }, {
#             'publishing_date': '2020-10-27T08:00:00-04:00',
#             'title': 'Test Multimedia 22',
#             'topics': ['Test Topic 2'],
#             'url': '/multimedia/multimedia-22/',
#         }, {
#             'publishing_date': '2020-09-03T08:00:00-04:00',
#             'title': 'Test Multimedia 18',
#             'topics': ['Test Topic 2'],
#             'url': '/multimedia/multimedia-18/',
#         }, {
#             'publishing_date': '2020-07-27T08:00:00-04:00',
#             'title': 'Test Multimedia 13',
#             'topics': ['Test Topic 2'],
#             'url': '/multimedia/multimedia-13/',
#         }, {
#             'publishing_date': '2020-06-19T08:00:00-04:00',
#             'title': 'Test Multimedia 9',
#             'topics': ['Test Topic 2'],
#             'url': '/multimedia/multimedia-9/',
#         }, {
#             'publishing_date': '2020-04-24T08:00:00-04:00',
#             'title': 'Test Multimedia 4',
#             'topics': ['Test Topic 2', 'Test Topic 3'],
#             'url': '/multimedia/multimedia-4/',
#         }])
#
#     def test_filter_topic_3_returns_200(self):
#         topic3 = TopicPage.objects.get(title='Test Topic 3')
#         res = self.client.get(f'{self.get_api_url(1)}&topics={topic3.id}')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 11)
#         self.assertEqual(len(resJson['items']), 11)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-12-10T08:00:00-05:00',
#             'title': 'Test Multimedia 27',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-27/',
#         }, {
#             'publishing_date': '2020-11-05T08:00:00-05:00',
#             'title': 'Test Multimedia 24',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-24/',
#         }, {
#             'publishing_date': '2020-10-28T08:00:00-04:00',
#             'title': 'Test Multimedia 23',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-23/',
#         }, {
#             'publishing_date': '2020-10-15T08:00:00-04:00',
#             'title': 'Test Multimedia 20',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-20/',
#         }, {
#             'publishing_date': '2020-08-11T08:00:00-04:00',
#             'title': 'Test Multimedia 15',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-15/',
#         }, {
#             'publishing_date': '2020-08-06T08:00:00-04:00',
#             'title': 'Test Multimedia 14',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-14/',
#         }, {
#             'publishing_date': '2020-07-06T08:00:00-04:00',
#             'title': 'Test Multimedia 11',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-11/',
#         }, {
#             'publishing_date': '2020-06-24T08:00:00-04:00',
#             'title': 'Test Multimedia 10',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-10/',
#         }, {
#             'publishing_date': '2020-05-07T08:00:00-04:00',
#             'title': 'Test Multimedia 5 - Big Tech',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-5/',
#         }, {
#             'publishing_date': '2020-04-24T08:00:00-04:00',
#             'title': 'Test Multimedia 4',
#             'topics': ['Test Topic 2', 'Test Topic 3'],
#             'url': '/multimedia/multimedia-4/',
#         }, {
#             'publishing_date': '2020-04-20T08:00:00-04:00',
#             'title': 'Test Multimedia 2',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-2/',
#         }])
#
#     def test_filter_multimedia_type_audio_returns_200(self):
#         res = self.client.get(f'{self.get_api_url(1)}&multimedia_type=audio')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 8)
#         self.assertEqual(len(resJson['items']), 8)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-11-24T08:00:00-05:00',
#             'title': 'Test Multimedia 25',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-25/',
#         }, {
#             'publishing_date': '2020-11-05T08:00:00-05:00',
#             'title': 'Test Multimedia 24',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-24/',
#         }, {
#             'publishing_date': '2020-09-03T08:00:00-04:00',
#             'title': 'Test Multimedia 18',
#             'topics': ['Test Topic 2'],
#             'url': '/multimedia/multimedia-18/',
#         }, {
#             'publishing_date': '2020-08-14T08:00:00-04:00',
#             'title': 'Test Multimedia 17',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-17/',
#         }, {
#             'publishing_date': '2020-08-11T08:00:00-04:00',
#             'title': 'Test Multimedia 15',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-15/',
#         }, {
#             'publishing_date': '2020-07-06T08:00:00-04:00',
#             'title': 'Test Multimedia 11',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-11/',
#         }, {
#             'publishing_date': '2020-06-19T08:00:00-04:00',
#             'title': 'Test Multimedia 9',
#             'topics': ['Test Topic 2'],
#             'url': '/multimedia/multimedia-9/',
#         }, {
#             'publishing_date': '2020-04-22T08:00:00-04:00',
#             'title': 'Test Multimedia 3',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-3/',
#         }])
#
#     def test_filter_multimedia_type_video_page_1_returns_200(self):
#         res = self.client.get(f'{self.get_api_url(1)}&multimedia_type=video')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 22)
#         self.assertEqual(len(resJson['items']), 18)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-12-25T08:00:00-05:00',
#             'title': 'Test Multimedia 30',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-30/',
#         }, {
#             'publishing_date': '2020-12-16T08:00:00-05:00',
#             'title': 'Test Multimedia 29',
#             'topics': ['Test Topic 2'],
#             'url': '/multimedia/multimedia-29/',
#         }, {
#             'publishing_date': '2020-12-11T08:00:00-05:00',
#             'title': 'Test Multimedia 28',
#             'topics': ['Test Topic 2'],
#             'url': '/multimedia/multimedia-28/',
#         }, {
#             'publishing_date': '2020-12-10T08:00:00-05:00',
#             'title': 'Test Multimedia 27',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-27/',
#         }, {
#             'publishing_date': '2020-12-07T08:00:00-05:00',
#             'title': 'Test Multimedia 26',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-26/',
#         }, {
#             'publishing_date': '2020-10-28T08:00:00-04:00',
#             'title': 'Test Multimedia 23',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-23/',
#         }, {
#             'publishing_date': '2020-10-27T08:00:00-04:00',
#             'title': 'Test Multimedia 22',
#             'topics': ['Test Topic 2'],
#             'url': '/multimedia/multimedia-22/',
#         }, {
#             'publishing_date': '2020-10-21T08:00:00-04:00',
#             'title': 'Test Multimedia 21',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-21/',
#         }, {
#             'publishing_date': '2020-10-15T08:00:00-04:00',
#             'title': 'Test Multimedia 20',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-20/',
#         }, {
#             'publishing_date': '2020-09-14T08:00:00-04:00',
#             'title': 'Test Multimedia 19',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-19/',
#         }, {
#             'publishing_date': '2020-08-12T08:00:00-04:00',
#             'title': 'Test Multimedia 16',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-16/',
#         }, {
#             'publishing_date': '2020-08-06T08:00:00-04:00',
#             'title': 'Test Multimedia 14',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-14/',
#         }, {
#             'publishing_date': '2020-07-27T08:00:00-04:00',
#             'title': 'Test Multimedia 13',
#             'topics': ['Test Topic 2'],
#             'url': '/multimedia/multimedia-13/',
#         }, {
#             'publishing_date': '2020-07-20T08:00:00-04:00',
#             'title': 'Test Multimedia 12 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-12/',
#         }, {
#             'publishing_date': '2020-06-24T08:00:00-04:00',
#             'title': 'Test Multimedia 10',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-10/',
#         }, {
#             'publishing_date': '2020-06-18T08:00:00-04:00',
#             'title': 'Test Multimedia 8',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-8/',
#         }, {
#             'publishing_date': '2020-06-16T08:00:00-04:00',
#             'title': 'Test Multimedia 7',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-7/',
#         }, {
#             'publishing_date': '2020-06-02T08:00:00-04:00',
#             'title': 'Test Multimedia 6',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-6/',
#         }])
#
#     def test_filter_multimedia_type_video_page_2_returns_200(self):
#         res = self.client.get(f'{self.get_api_url(2)}&multimedia_type=video')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 22)
#         self.assertEqual(len(resJson['items']), 4)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-05-07T08:00:00-04:00',
#             'title': 'Test Multimedia 5 - Big Tech',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-5/',
#         }, {
#             'publishing_date': '2020-04-24T08:00:00-04:00',
#             'title': 'Test Multimedia 4',
#             'topics': ['Test Topic 2', 'Test Topic 3'],
#             'url': '/multimedia/multimedia-4/',
#         }, {
#             'publishing_date': '2020-04-20T08:00:00-04:00',
#             'title': 'Test Multimedia 2',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-2/',
#         }, {
#             'publishing_date': '2020-02-04T08:00:00-05:00',
#             'title': 'Test Multimedia 1',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-1/',
#         }])
#
#     def test_search_and_filter_topics_returns_200(self):
#         topic3 = TopicPage.objects.get(title='Test Topic 3')
#         res = self.client.get(f'{self.get_api_url(1)}&search=big+tech&topics={topic3.id}')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 2)
#         self.assertEqual(len(resJson['items']), 2)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-05-07T08:00:00-04:00',
#             'title': 'Test Multimedia 5 - Big Tech',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-5/',
#         }, {
#             'publishing_date': '2020-10-28T08:00:00-04:00',
#             'title': 'Test Multimedia 23',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-23/',
#         }])
#
#     def test_search_and_filter_multimedia_type_video_returns_200(self):
#         res = self.client.get(f'{self.get_api_url(1)}&search=big+tech&multimedia_type=video')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 3)
#         self.assertEqual(len(resJson['items']), 3)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-07-20T08:00:00-04:00',
#             'title': 'Test Multimedia 12 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/multimedia/multimedia-12/',
#         }, {
#             'publishing_date': '2020-05-07T08:00:00-04:00',
#             'title': 'Test Multimedia 5 - Big Tech',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-5/',
#         }, {
#             'publishing_date': '2020-10-28T08:00:00-04:00',
#             'title': 'Test Multimedia 23',
#             'topics': ['Test Topic 3'],
#             'url': '/multimedia/multimedia-23/',
#         }])
#
#     def test_search_and_filter_multimedia_type_audio_returns_200(self):
#         res = self.client.get(f'{self.get_api_url(1)}&search=big+tech&multimedia_type=audio')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 0)
#         self.assertEqual(len(resJson['items']), 0)
