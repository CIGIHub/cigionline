from home.models import HomePage, Think7HomePage
from wagtail.test.utils import WagtailPageTestCase

from .models import (
    PublicationListPage,
    PublicationPage,
    PublicationSeriesListPage,
    PublicationSeriesPage,
    PublicationTypePage,
    T7PublicationPage,
)

from articles.models import ArticleSeriesListPage, ArticleTypePage


class PublicationListPageTests(WagtailPageTestCase):
    def test_publicationlistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            PublicationListPage,
            {HomePage, Think7HomePage},
        )

    def test_publicationlistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            PublicationListPage,
            {PublicationPage, PublicationTypePage, PublicationSeriesListPage, ArticleSeriesListPage, ArticleTypePage, T7PublicationPage},
        )


class PublicationPageTests(WagtailPageTestCase):
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


class PublicationSeriesListPageTests(WagtailPageTestCase):
    def test_publicationserieslistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            PublicationSeriesListPage,
            {HomePage, PublicationListPage},
        )

    def test_publicationserieslistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            PublicationSeriesListPage,
            {PublicationSeriesPage},
        )


class PublicationSeriesPageTests(WagtailPageTestCase):
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


class PublicationTypePageTests(WagtailPageTestCase):
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
