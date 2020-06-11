from careers.models import JobPostingListPage
from people.models import PeoplePage, PersonListPage
from research.models import TopicListPage
from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import nested_form_data

from .models import AnnualReportListPage, AnnualReportPage, BasicPage, FundingPage, HomePage


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
            {BasicPage, HomePage}
        )

    def test_basicpage_child_page_types(self):
        """
        Verify allowed child page types.
        """
        self.assertAllowedSubpageTypes(
            BasicPage,
            {AnnualReportListPage, BasicPage, FundingPage, PersonListPage}
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


class HomePageTests(WagtailPageTests):
    def test_homepage_child_page_types(self):
        """
        Verify allowed child page types.
        """
        self.assertAllowedSubpageTypes(
            HomePage,
            {
                BasicPage,
                JobPostingListPage,
                PeoplePage,
                PersonListPage,
                TopicListPage,
            }
        )

    def test_cannot_create_homepage(self):
        """
        Test that we can't create a second home page. Wagtail will create a home
        page object on initialization so we don't need to create one first.
        """
        root_page = Page.objects.get(pk=1)
        try:
            self.assertCanCreate(root_page, HomePage, nested_form_data({
                'title': 'Home',
            }))
            self.fail('Expected to error')
        except AssertionError:
            pass
