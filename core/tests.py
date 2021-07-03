from annual_reports.models import AnnualReportListPage
from careers.models import JobPostingListPage
from home.models import HomePage
from people.models import PersonListPage
from research.models import (
    ProjectPage,
)
from wagtail.tests.utils import WagtailPageTests

from .models import (
    BasicPage,
    FundingPage,
    PrivacyNoticePage,
    TwentiethPage,
)


class BasicPageTests(WagtailPageTests):
    def test_basicpage_parent_page_types(self):
        """
        Verify allowed parent page types.
        """
        self.assertAllowedParentPageTypes(
            BasicPage,
            {BasicPage, HomePage, JobPostingListPage}
        )

    def test_basicpage_child_page_types(self):
        """
        Verify allowed child page types.
        """
        self.assertAllowedSubpageTypes(
            BasicPage,
            {AnnualReportListPage, BasicPage, FundingPage, PersonListPage, ProjectPage, TwentiethPage}
        )


class FundingPageTests(WagtailPageTests):
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


class PrivacyNoticePageTests(WagtailPageTests):
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
