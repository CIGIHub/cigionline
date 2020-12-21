from core.models import HomePage
from research.models import TopicPage
from wagtail.tests.utils import WagtailPageTests

from .models import EventListPage, EventPage


class EventListPageTests(WagtailPageTests):
    def test_eventlistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            EventListPage,
            {HomePage},
        )

    def test_eventlistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            EventListPage,
            {EventPage},
        )


class EventPageTests(WagtailPageTests):
    def test_eventpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            EventPage,
            {EventListPage},
        )

    def test_eventpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            EventPage,
            {},
        )


class EventPageViewSetTests(WagtailPageTests):
    fixtures = ['events_search_table.json']
    limit = 24

    def get_api_url(self, page):
        offset = (page - 1) * self.limit
        return f'/api/events/?limit={self.limit}&offset={offset}&fields=publishing_date,title,topics(title,url),url'

    def verify_res_items(self, responseItems, expectedItems):
        for i in range(len(expectedItems)):
            self.assertEqual(responseItems[i]['title'], expectedItems[i]['title'])
            self.assertEqual(responseItems[i]['url'], expectedItems[i]['url'])
            self.assertEqual(responseItems[i]['publishing_date'], expectedItems[i]['publishing_date'])

            self.assertEqual(len(responseItems[i]['topics']), len(expectedItems[i]['topics']), f'Length of topics: {expectedItems[i]["title"]}')
            # Verify that the expected topic titles were returned in the response
            for topicTitle in expectedItems[i]['topics']:
                self.assertTrue(any(topic['title'] == topicTitle for topic in responseItems[i]['topics']), f'Could not find topic:{topicTitle} for publication:{expectedItems[i]["title"]}')

    def test_page_1_query_returns_200(self):
        res = self.client.get(self.get_api_url(1))
        self.assertEqual(res.status_code, 200)
        resJson = res.json()
        self.assertEqual(resJson['meta']['total_count'], 30)
        self.assertEqual(len(resJson['items']), 24)

        self.verify_res_items(resJson['items'], [{
            'publishing_date': '2020-12-31T08:00:00-05:00',
            'title': 'Test Event 30',
            'topics': ['Test Topic 3'],
            'url': '/events/event-30/',
        }, {
            'publishing_date': '2020-12-30T08:00:00-05:00',
            'title': 'Test Event 29',
            'topics': ['Test Topic 2'],
            'url': '/events/event-29/',
        }, {
            'publishing_date': '2020-12-25T08:00:00-05:00',
            'title': 'Test Event 28',
            'topics': ['Test Topic 1', 'Test Topic 2'],
            'url': '/events/event-28/',
        }, {
            'publishing_date': '2020-12-15T08:00:00-05:00',
            'title': 'Test Event 27',
            'topics': ['Test Topic 1'],
            'url': '/events/event-27/',
        }, {
            'publishing_date': '2020-12-04T08:00:00-05:00',
            'title': 'Test Event 26',
            'topics': ['Test Topic 1'],
            'url': '/events/event-26/',
        }, {
            'publishing_date': '2020-11-17T08:00:00-05:00',
            'title': 'Test Event 25',
            'topics': ['Test Topic 3'],
            'url': '/events/event-25/',
        }, {
            'publishing_date': '2020-10-30T08:00:00-04:00',
            'title': 'Test Event 24',
            'topics': ['Test Topic 1'],
            'url': '/events/event-24/',
        }, {
            'publishing_date': '2020-10-27T08:00:00-04:00',
            'title': 'Test Event 23',
            'topics': ['Test Topic 3'],
            'url': '/events/event-23/',
        }, {
            'publishing_date': '2020-09-24T08:00:00-04:00',
            'title': 'Test Event 22 - Big Tech',
            'topics': ['Test Topic 3'],
            'url': '/events/event-22/',
        }, {
            'publishing_date': '2020-09-18T08:00:00-04:00',
            'title': 'Test Event 21',
            'topics': ['Test Topic 2'],
            'url': '/events/event-21/',
        }, {
            'publishing_date': '2020-09-16T08:00:00-04:00',
            'title': 'Test Event 20',
            'topics': ['Test Topic 1'],
            'url': '/events/event-20/',
        }, {
            'publishing_date': '2020-09-08T08:00:00-04:00',
            'title': 'Test Event 19',
            'topics': ['Test Topic 2', 'Test Topic 3'],
            'url': '/events/event-19/',
        }, {
            'publishing_date': '2020-09-01T08:00:00-04:00',
            'title': 'Test Event 18',
            'topics': ['Test Topic 1'],
            'url': '/events/event-18/',
        }, {
            'publishing_date': '2020-08-04T08:00:00-04:00',
            'title': 'Test Event 17',
            'topics': ['Test Topic 1'],
            'url': '/events/event-17/',
        }, {
            'publishing_date': '2020-07-09T08:00:00-04:00',
            'title': 'Test Event 16',
            'topics': ['Test Topic 1'],
            'url': '/events/event-16/',
        }, {
            'publishing_date': '2020-06-26T08:00:00-04:00',
            'title': 'Test Event 15',
            'topics': ['Test Topic 2'],
            'url': '/events/event-15/',
        }, {
            'publishing_date': '2020-06-15T08:00:00-04:00',
            'title': 'Test Event 14',
            'topics': ['Test Topic 1'],
            'url': '/events/event-14/',
        }, {
            'publishing_date': '2020-05-25T08:00:00-04:00',
            'title': 'Test Event 13',
            'topics': ['Test Topic 1'],
            'url': '/events/event-13/',
        }, {
            'publishing_date': '2020-05-21T08:00:00-04:00',
            'title': 'Test Event 12',
            'topics': ['Test Topic 3'],
            'url': '/events/event-12/',
        }, {
            'publishing_date': '2020-04-23T08:00:00-04:00',
            'title': 'Test Event 11',
            'topics': ['Test Topic 3'],
            'url': '/events/event-11/',
        }, {
            'publishing_date': '2020-04-13T08:00:00-04:00',
            'title': 'Test Event 10',
            'topics': ['Test Topic 3'],
            'url': '/events/event-10/',
        }, {
            'publishing_date': '2020-03-18T08:00:00-04:00',
            'title': 'Test Event 9',
            'topics': ['Test Topic 1'],
            'url': '/events/event-9/',
        }, {
            'publishing_date': '2020-03-12T08:00:00-04:00',
            'title': 'Test Event 8',
            'topics': ['Test Topic 2'],
            'url': '/events/event-8/',
        }, {
            'publishing_date': '2020-02-21T08:00:00-05:00',
            'title': 'Test Event 7',
            'topics': ['Test Topic 2'],
            'url': '/events/event-7/',
        }])

    def test_page_2_query_returns_200(self):
        res = self.client.get(self.get_api_url(2))
        self.assertEqual(res.status_code, 200)
        resJson = res.json()
        self.assertEqual(resJson['meta']['total_count'], 30)
        self.assertEqual(len(resJson['items']), 6)

        self.verify_res_items(resJson['items'], [{
            'publishing_date': '2020-02-20T08:00:00-05:00',
            'title': 'Test Event 6',
            'topics': ['Test Topic 3'],
            'url': '/events/event-6/',
        }, {
            'publishing_date': '2020-02-19T08:00:00-05:00',
            'title': 'Test Event 5',
            'topics': ['Test Topic 3'],
            'url': '/events/event-5/',
        }, {
            'publishing_date': '2020-02-13T08:00:00-05:00',
            'title': 'Test Event 4',
            'topics': ['Test Topic 2'],
            'url': '/events/event-4/',
        }, {
            'publishing_date': '2020-01-30T08:00:00-05:00',
            'title': 'Test Event 3 - Big Tech',
            'topics': ['Test Topic 1'],
            'url': '/events/event-3/',
        }, {
            'publishing_date': '2020-01-15T08:00:00-05:00',
            'title': 'Test Event 2',
            'topics': ['Test Topic 1'],
            'url': '/events/event-2/',
        }, {
            'publishing_date': '2020-01-02T08:00:00-05:00',
            'title': 'Test Event 1',
            'topics': ['Test Topic 1'],
            'url': '/events/event-1/',
        }])

    def test_page_3_returns_200(self):
        res = self.client.get(self.get_api_url(3))
        self.assertEqual(res.status_code, 200)
        resJson = res.json()
        self.assertEqual(resJson['meta']['total_count'], 30)
        self.assertEqual(len(resJson['items']), 0)

    def test_search_query_returns_200(self):
        res = self.client.get(f'{self.get_api_url(1)}&search=big+tech')
        self.assertEqual(res.status_code, 200)
        resJson = res.json()
        self.assertEqual(resJson['meta']['total_count'], 3)
        self.assertEqual(len(resJson['items']), 3)

        self.verify_res_items(resJson['items'], [{
            'publishing_date': '2020-09-24T08:00:00-04:00',
            'title': 'Test Event 22 - Big Tech',
            'topics': ['Test Topic 3'],
            'url': '/events/event-22/',
        }, {
            'publishing_date': '2020-06-15T08:00:00-04:00',
            'title': 'Test Event 14',
            'topics': ['Test Topic 1'],
            'url': '/events/event-14/',
        }, {
            'publishing_date': '2020-01-30T08:00:00-05:00',
            'title': 'Test Event 3 - Big Tech',
            'topics': ['Test Topic 1'],
            'url': '/events/event-3/',
        }])

    def test_filter_topic_1_returns_200(self):
        topic1 = TopicPage.objects.get(title='Test Topic 1')
        res = self.client.get(f'{self.get_api_url(1)}&topics={topic1.id}')
        self.assertEqual(res.status_code, 200)
        resJson = res.json()
        self.assertEqual(resJson['meta']['total_count'], 14)
        self.assertEqual(len(resJson['items']), 14)

        self.verify_res_items(resJson['items'], [{
            'publishing_date': '2020-12-25T08:00:00-05:00',
            'title': 'Test Event 28',
            'topics': ['Test Topic 1', 'Test Topic 2'],
            'url': '/events/event-28/',
        }, {
            'publishing_date': '2020-12-15T08:00:00-05:00',
            'title': 'Test Event 27',
            'topics': ['Test Topic 1'],
            'url': '/events/event-27/',
        }, {
            'publishing_date': '2020-12-04T08:00:00-05:00',
            'title': 'Test Event 26',
            'topics': ['Test Topic 1'],
            'url': '/events/event-26/',
        }, {
            'publishing_date': '2020-10-30T08:00:00-04:00',
            'title': 'Test Event 24',
            'topics': ['Test Topic 1'],
            'url': '/events/event-24/',
        }, {
            'publishing_date': '2020-09-16T08:00:00-04:00',
            'title': 'Test Event 20',
            'topics': ['Test Topic 1'],
            'url': '/events/event-20/',
        }, {
            'publishing_date': '2020-09-01T08:00:00-04:00',
            'title': 'Test Event 18',
            'topics': ['Test Topic 1'],
            'url': '/events/event-18/',
        }, {
            'publishing_date': '2020-08-04T08:00:00-04:00',
            'title': 'Test Event 17',
            'topics': ['Test Topic 1'],
            'url': '/events/event-17/',
        }, {
            'publishing_date': '2020-07-09T08:00:00-04:00',
            'title': 'Test Event 16',
            'topics': ['Test Topic 1'],
            'url': '/events/event-16/',
        }, {
            'publishing_date': '2020-06-15T08:00:00-04:00',
            'title': 'Test Event 14',
            'topics': ['Test Topic 1'],
            'url': '/events/event-14/',
        }, {
            'publishing_date': '2020-05-25T08:00:00-04:00',
            'title': 'Test Event 13',
            'topics': ['Test Topic 1'],
            'url': '/events/event-13/',
        }, {
            'publishing_date': '2020-03-18T08:00:00-04:00',
            'title': 'Test Event 9',
            'topics': ['Test Topic 1'],
            'url': '/events/event-9/',
        }, {
            'publishing_date': '2020-01-30T08:00:00-05:00',
            'title': 'Test Event 3 - Big Tech',
            'topics': ['Test Topic 1'],
            'url': '/events/event-3/',
        }, {
            'publishing_date': '2020-01-15T08:00:00-05:00',
            'title': 'Test Event 2',
            'topics': ['Test Topic 1'],
            'url': '/events/event-2/',
        }, {
            'publishing_date': '2020-01-02T08:00:00-05:00',
            'title': 'Test Event 1',
            'topics': ['Test Topic 1'],
            'url': '/events/event-1/',
        }])

    def test_filter_topic_2_returns_200(self):
        topic2 = TopicPage.objects.get(title='Test Topic 2')
        res = self.client.get(f'{self.get_api_url(1)}&topics={topic2.id}')
        self.assertEqual(res.status_code, 200)
        resJson = res.json()
        self.assertEqual(resJson['meta']['total_count'], 8)
        self.assertEqual(len(resJson['items']), 8)

        self.verify_res_items(resJson['items'], [{
            'publishing_date': '2020-12-30T08:00:00-05:00',
            'title': 'Test Event 29',
            'topics': ['Test Topic 2'],
            'url': '/events/event-29/',
        }, {
            'publishing_date': '2020-12-25T08:00:00-05:00',
            'title': 'Test Event 28',
            'topics': ['Test Topic 1', 'Test Topic 2'],
            'url': '/events/event-28/',
        }, {
            'publishing_date': '2020-09-18T08:00:00-04:00',
            'title': 'Test Event 21',
            'topics': ['Test Topic 2'],
            'url': '/events/event-21/',
        }, {
            'publishing_date': '2020-09-08T08:00:00-04:00',
            'title': 'Test Event 19',
            'topics': ['Test Topic 2', 'Test Topic 3'],
            'url': '/events/event-19/',
        }, {
            'publishing_date': '2020-06-26T08:00:00-04:00',
            'title': 'Test Event 15',
            'topics': ['Test Topic 2'],
            'url': '/events/event-15/',
        }, {
            'publishing_date': '2020-03-12T08:00:00-04:00',
            'title': 'Test Event 8',
            'topics': ['Test Topic 2'],
            'url': '/events/event-8/',
        }, {
            'publishing_date': '2020-02-21T08:00:00-05:00',
            'title': 'Test Event 7',
            'topics': ['Test Topic 2'],
            'url': '/events/event-7/',
        }, {
            'publishing_date': '2020-02-13T08:00:00-05:00',
            'title': 'Test Event 4',
            'topics': ['Test Topic 2'],
            'url': '/events/event-4/',
        }])

    def test_filter_topic_3_returns_200(self):
        topic3 = TopicPage.objects.get(title='Test Topic 3')
        res = self.client.get(f'{self.get_api_url(1)}&topics={topic3.id}')
        self.assertEqual(res.status_code, 200)
        resJson = res.json()
        self.assertEqual(resJson['meta']['total_count'], 10)
        self.assertTrue(len(resJson['items']), 10)

        self.verify_res_items(resJson['items'], [{
            'publishing_date': '2020-12-31T08:00:00-05:00',
            'title': 'Test Event 30',
            'topics': ['Test Topic 3'],
            'url': '/events/event-30/',
        }, {
            'publishing_date': '2020-11-17T08:00:00-05:00',
            'title': 'Test Event 25',
            'topics': ['Test Topic 3'],
            'url': '/events/event-25/',
        }, {
            'publishing_date': '2020-10-27T08:00:00-04:00',
            'title': 'Test Event 23',
            'topics': ['Test Topic 3'],
            'url': '/events/event-23/',
        }, {
            'publishing_date': '2020-09-24T08:00:00-04:00',
            'title': 'Test Event 22 - Big Tech',
            'topics': ['Test Topic 3'],
            'url': '/events/event-22/',
        }, {
            'publishing_date': '2020-09-08T08:00:00-04:00',
            'title': 'Test Event 19',
            'topics': ['Test Topic 2', 'Test Topic 3'],
            'url': '/events/event-19/',
        }, {
            'publishing_date': '2020-05-21T08:00:00-04:00',
            'title': 'Test Event 12',
            'topics': ['Test Topic 3'],
            'url': '/events/event-12/',
        }, {
            'publishing_date': '2020-04-23T08:00:00-04:00',
            'title': 'Test Event 11',
            'topics': ['Test Topic 3'],
            'url': '/events/event-11/',
        }, {
            'publishing_date': '2020-04-13T08:00:00-04:00',
            'title': 'Test Event 10',
            'topics': ['Test Topic 3'],
            'url': '/events/event-10/',
        }, {
            'publishing_date': '2020-02-20T08:00:00-05:00',
            'title': 'Test Event 6',
            'topics': ['Test Topic 3'],
            'url': '/events/event-6/',
        }, {
            'publishing_date': '2020-02-19T08:00:00-05:00',
            'title': 'Test Event 5',
            'topics': ['Test Topic 3'],
            'url': '/events/event-5/',
        }])

    def test_search_and_filter_topics_returns_200(self):
        topic1 = TopicPage.objects.get(title='Test Topic 1')
        res = self.client.get(f'{self.get_api_url(1)}&search=big+tech&topics={topic1.id}')
        self.assertEqual(res.status_code, 200)
        resJson = res.json()
        self.assertEqual(resJson['meta']['total_count'], 2)
        self.assertEqual(len(resJson['items']), 2)

        self.verify_res_items(resJson['items'], [{
            'publishing_date': '2020-06-15T08:00:00-04:00',
            'title': 'Test Event 14',
            'topics': ['Test Topic 1'],
            'url': '/events/event-14/',
        }, {
            'publishing_date': '2020-01-30T08:00:00-05:00',
            'title': 'Test Event 3 - Big Tech',
            'topics': ['Test Topic 1'],
            'url': '/events/event-3/',
        }])
