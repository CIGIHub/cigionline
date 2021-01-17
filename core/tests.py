from careers.models import JobPostingListPage
from home.models import HomePage
from people.models import PersonListPage
from research.models import (
    ProjectPage,
)
from wagtail.tests.utils import WagtailPageTests

from .models import (
    AnnualReportListPage,
    AnnualReportPage,
    BasicPage,
    ContactPage,
    FundingPage,
    PrivacyNoticePage,
)


class AnnualReportListPageTests(WagtailPageTests):
    def test_annualreportlistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            AnnualReportListPage,
            {BasicPage},
        )

    def test_annualreportlistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            AnnualReportListPage,
            {AnnualReportPage},
        )


class AnnualReportPageTests(WagtailPageTests):
    def test_annualreportpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            AnnualReportPage,
            {AnnualReportListPage},
        )

    def test_annualreportpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            AnnualReportPage,
            {},
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
            {AnnualReportListPage, BasicPage, FundingPage, PersonListPage, ProjectPage}
        )


class ContactPageTests(WagtailPageTests):
    def test_contactpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            ContactPage,
            {HomePage},
        )

    def test_contactpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            ContactPage,
            {},
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
