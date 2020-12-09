from core.models import HomePage
from wagtail.tests.utils import WagtailPageTests

from .models import (
    MultimediaListPage,
    MultimediaPage,
    MultimediaSeriesListPage,
    MultimediaSeriesPage,
)


class MultimediaListPageTests(WagtailPageTests):
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


class MultimediaPageTests(WagtailPageTests):
    def test_multimediapage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            MultimediaPage,
            {MultimediaListPage},
        )

    def test_multimediapage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            MultimediaPage,
            {},
        )


class MultimediaSeriesListPageTests(WagtailPageTests):
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


class MultimediaSeriesPageTests(WagtailPageTests):
    def test_multimediaseriespage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            MultimediaSeriesPage,
            {HomePage, MultimediaSeriesListPage},
        )

    def test_multimediaseriespage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            MultimediaSeriesPage,
            {},
        )


class MultimediaPageViewSetTests(WagtailPageTests):
    fixtures = ['multimedia_search_table.json']
    limit = 18

    def setUp(self):
        home_page = HomePage.objects.get()
        home_page.numchild = 2
        home_page.save()

    def get_api_url(self, page):
        offset = (page - 1) * self.limit
        return f'/api/multimedia/?limit={self.limit}&offset={offset}&fields=title,url,publishing_date,topics(title,url)'

    def verify_res_items(self, responseItems, expectedItems):
        for i in range(len(expectedItems)):
            self.assertEqual(responseItems[i]['publishing_date'], expectedItems[i]['publishing_date'])
            self.assertEqual(responseItems[i]['title'], expectedItems[i]['title'])
            self.assertEqual(responseItems[i]['url'], expectedItems[i]['url'])

            self.assertEqual(len(responseItems[i]['topics']), len(expectedItems[i]['topics']))
            # Verify that the expected topic titles were returned in the response
            for topicTitle in expectedItems[i]['topics']:
                self.assertTrue(any(topic['title'] == topicTitle for topic in responseItems[i]['topics']))

    def test_page_1_query_returns_200(self):
        res = self.client.get(self.get_api_url(1))
        self.assertEqual(res.status_code, 200)
        resJson = res.json()
        self.assertEqual(resJson['meta']['total_count'], 30)
        self.assertEqual(len(resJson['items']), 18)

        self.verify_res_items(resJson['items'], [{
            'publishing_date': '2020-12-25T08:00:00-05:00',
            'title': 'Test Multimedia 30',
            'topics': ['Test Topic 1'],
            'url': '/multimedia/multimedia-30/',
        }, {
            'publishing_date': '2020-12-16T08:00:00-05:00',
            'title': 'Test Multimedia 29',
            'topics': ['Test Topic 2'],
            'url': '/multimedia/multimedia-29/',
        }, {
            'publishing_date': '2020-12-11T08:00:00-05:00',
            'title': 'Test Multimedia 28',
            'topics': ['Test Topic 2'],
            'url': '/multimedia/multimedia-28/',
        }, {
            'publishing_date': '2020-12-10T08:00:00-05:00',
            'title': 'Test Multimedia 27',
            'topics': ['Test Topic 3'],
            'url': '/multimedia/multimedia-27/',
        }, {
            'publishing_date': '2020-12-07T08:00:00-05:00',
            'title': 'Test Multimedia 26',
            'topics': ['Test Topic 1'],
            'url': '/multimedia/multimedia-26/',
        }, {
            'publishing_date': '2020-11-24T08:00:00-05:00',
            'title': 'Test Multimedia 25',
            'topics': ['Test Topic 1'],
            'url': '/multimedia/multimedia-25/',
        }, {
            'publishing_date': '2020-11-05T08:00:00-05:00',
            'title': 'Test Multimedia 24',
            'topics': ['Test Topic 3'],
            'url': '/multimedia/multimedia-24/',
        }, {
            'publishing_date': '2020-10-28T08:00:00-04:00',
            'title': 'Test Multimedia 23',
            'topics': ['Test Topic 3'],
            'url': '/multimedia/multimedia-23/',
        }, {
            'publishing_date': '2020-10-27T08:00:00-04:00',
            'title': 'Test Multimedia 22',
            'topics': ['Test Topic 2'],
            'url': '/multimedia/multimedia-22/',
        }, {
            'publishing_date': '2020-10-21T08:00:00-04:00',
            'title': 'Test Multimedia 21',
            'topics': ['Test Topic 1'],
            'url': '/multimedia/multimedia-21/',
        }, {
            'publishing_date': '2020-10-15T08:00:00-04:00',
            'title': 'Test Multimedia 20',
            'topics': ['Test Topic 3'],
            'url': '/multimedia/multimedia-20/',
        }, {
            'publishing_date': '2020-09-14T08:00:00-04:00',
            'title': 'Test Multimedia 19',
            'topics': ['Test Topic 1'],
            'url': '/multimedia/multimedia-19/',
        }, {
            'publishing_date': '2020-09-03T08:00:00-04:00',
            'title': 'Test Multimedia 18',
            'topics': ['Test Topic 2'],
            'url': '/multimedia/multimedia-18/',
        }, {
            'publishing_date': '2020-08-14T08:00:00-04:00',
            'title': 'Test Multimedia 17',
            'topics': ['Test Topic 1'],
            'url': '/multimedia/multimedia-17/',
        }, {
            'publishing_date': '2020-08-12T08:00:00-04:00',
            'title': 'Test Multimedia 16',
            'topics': ['Test Topic 1'],
            'url': '/multimedia/multimedia-16/',
        }, {
            'publishing_date': '2020-08-11T08:00:00-04:00',
            'title': 'Test Multimedia 15',
            'topics': ['Test Topic 3'],
            'url': '/multimedia/multimedia-15/',
        }, {
            'publishing_date': '2020-08-06T08:00:00-04:00',
            'title': 'Test Multimedia 14',
            'topics': ['Test Topic 3'],
            'url': '/multimedia/multimedia-14/',
        }, {
            'publishing_date': '2020-07-27T08:00:00-04:00',
            'title': 'Test Multimedia 13',
            'topics': ['Test Topic 2'],
            'url': '/multimedia/multimedia-13/',
        }])
