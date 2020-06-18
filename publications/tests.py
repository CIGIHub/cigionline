from core.models import HomePage
from wagtail.tests.utils import WagtailPageTests

from .models import PublicationListPage, PublicationPage


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
