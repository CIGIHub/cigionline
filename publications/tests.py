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
