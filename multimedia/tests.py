from core.models import HomePage
from wagtail.tests.utils import WagtailPageTests

from .models import (
    MultimediaListPage,
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
