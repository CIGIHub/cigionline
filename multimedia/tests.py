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

    def setUp(self):
        home_page = HomePage.objects.get()
        home_page.numchild = 2
        home_page.save()

    def test_page_1_query_returns_200(self):
        res = self.client.get('/api/multimedia/?limit=18&offset=0&fields=title,url,publishing_date,topics(title,url)')
        self.assertEqual(res.status_code, 200)
        resJson = res.json()
        self.assertEqual(resJson['meta']['total_count'], 30)
        self.assertEqual(len(resJson['items']), 18)

        resExpected = [{
            'publishing_date': '2020-12-25T08:00:00-05:00',
            'title': 'Test Multimedia 30',
            'url': '/multimedia/multimedia-30/',
        }, {
            'publishing_date': '2020-12-16T08:00:00-05:00',
            'title': 'Test Multimedia 29',
            'url': '/multimedia/multimedia-29/',
        }, {
            'publishing_date': '2020-12-11T08:00:00-05:00',
            'title': 'Test Multimedia 28',
            'url': '/multimedia/multimedia-28/',
        }, {
            'publishing_date': '2020-12-10T08:00:00-05:00',
            'title': 'Test Multimedia 27',
            'url': '/multimedia/multimedia-27/',
        }, {
            'publishing_date': '2020-12-07T08:00:00-05:00',
            'title': 'Test Multimedia 26',
            'url': '/multimedia/multimedia-26/',
        }, {
            'publishing_date': '2020-11-24T08:00:00-05:00',
            'title': 'Test Multimedia 25',
            'url': '/multimedia/multimedia-25/',
        }, {
            'publishing_date': '2020-11-05T08:00:00-05:00',
            'title': 'Test Multimedia 24',
            'url': '/multimedia/multimedia-24/',
        }, {
            'publishing_date': '2020-10-28T08:00:00-04:00',
            'title': 'Test Multimedia 23',
            'url': '/multimedia/multimedia-23/',
        }, {
            'publishing_date': '2020-10-27T08:00:00-04:00',
            'title': 'Test Multimedia 22',
            'url': '/multimedia/multimedia-22/',
        }, {
            'publishing_date': '2020-10-21T08:00:00-04:00',
            'title': 'Test Multimedia 21',
            'url': '/multimedia/multimedia-21/',
        }, {
            'publishing_date': '2020-10-15T08:00:00-04:00',
            'title': 'Test Multimedia 20',
            'url': '/multimedia/multimedia-20/',
        }, {
            'publishing_date': '2020-09-14T08:00:00-04:00',
            'title': 'Test Multimedia 19',
            'url': '/multimedia/multimedia-19/',
        }, {
            'publishing_date': '2020-09-03T08:00:00-04:00',
            'title': 'Test Multimedia 18',
            'url': '/multimedia/multimedia-18/',
        }, {
            'publishing_date': '2020-08-14T08:00:00-04:00',
            'title': 'Test Multimedia 17',
            'url': '/multimedia/multimedia-17/',
        }, {
            'publishing_date': '2020-08-12T08:00:00-04:00',
            'title': 'Test Multimedia 16',
            'url': '/multimedia/multimedia-16/',
        }, {
            'publishing_date': '2020-08-11T08:00:00-04:00',
            'title': 'Test Multimedia 15',
            'url': '/multimedia/multimedia-15/',
        }, {
            'publishing_date': '2020-08-06T08:00:00-04:00',
            'title': 'Test Multimedia 14',
            'url': '/multimedia/multimedia-14/',
        }, {
            'publishing_date': '2020-07-27T08:00:00-04:00',
            'title': 'Test Multimedia 13',
            'url': '/multimedia/multimedia-13/',
        }]

        for i in range(18):
            self.assertEqual(resJson['items'][i]['publishing_date'], resExpected[i]['publishing_date'])
            self.assertEqual(resJson['items'][i]['title'], resExpected[i]['title'])
            self.assertEqual(resJson['items'][i]['url'], resExpected[i]['url'])
        # print(response.json())
