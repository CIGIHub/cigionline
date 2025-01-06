from annual_reports.models import AnnualReportListPage
from careers.models import JobPostingListPage
from home.models import HomePage, Think7HomePage
from people.models import PersonListPage
from research.models import (
    ProjectPage,
)
from wagtail.test.utils import WagtailPageTestCase

from .models import (
    BasicPage,
    FundingPage,
    PrivacyNoticePage,
    TwentiethPage,
    TwentiethPageSingleton,
)


class BasicPageTests(WagtailPageTestCase):
    def test_basicpage_parent_page_types(self):
        """
        Verify allowed parent page types.
        """
        self.assertAllowedParentPageTypes(
            BasicPage,
            {BasicPage, HomePage, JobPostingListPage, Think7HomePage}
        )

    def test_basicpage_child_page_types(self):
        """
        Verify allowed child page types.
        """
        self.assertAllowedSubpageTypes(
            BasicPage,
            {AnnualReportListPage, BasicPage, FundingPage, PersonListPage, ProjectPage, TwentiethPage, TwentiethPageSingleton}
        )


class FundingPageTests(WagtailPageTestCase):
    def test_fundingpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            FundingPage,
            {BasicPage},
        )

    def test_fundingpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            FundingPage,
            {},
        )


class PrivacyNoticePageTests(WagtailPageTestCase):
    def test_privacynoticepage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            PrivacyNoticePage,
            {HomePage},
        )

    def test_privacynoticepage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            PrivacyNoticePage,
            {},
        )
