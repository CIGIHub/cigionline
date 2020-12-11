from core.models import HomePage
from wagtail.tests.utils import WagtailPageTests

from .models import (
    PublicationListPage,
    PublicationPage,
    PublicationSeriesListPage,
    PublicationSeriesPage,
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
            {PublicationPage},
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


class PublicationPageViewSetTests(WagtailPageTests):
    fixtures = ['publications_search_table.json']
    limit = 24

    def setUp(self):
        home_page = HomePage.objects.get()
        home_page.numchild = 2
        home_page.save()

    def get_api_url(self, page):
        offset = (page - 1) * self.limit
        return f'/api/publications/?limit={self.limit}&offset={offset}&fields=authors,pdf_downloads,publishing_date,title,topics(title,url),url'

    def test_page_1_query_returns_200(self):
        res = self.client.get(self.get_api_url(1))
        self.assertEqual(res.status_code, 200)
        resJson = res.json()
        self.assertEqual(resJson['meta']['total_count'], 30)
        self.assertEqual(len(resJson['items']), 24)
