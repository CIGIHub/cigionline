from articles.models import (
    ArticleLandingPage,
    ArticleListPage,
    ArticleSeriesListPage,
    ArticleSeriesPage,
    MediaLandingPage,
)
from careers.models import JobPostingListPage
from events.models import EventListPage
from multimedia.models import MultimediaListPage, MultimediaSeriesListPage, MultimediaSeriesPage
from newsletters.models import NewsletterListPage
from people.models import PeoplePage, PersonListPage
from publications.models import PublicationListPage, PublicationSeriesListPage
from research.models import (
    ProjectListPage,
    ProjectPage,
    ResearchLandingPage,
    TopicListPage,
)
from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import nested_form_data

from .models import (
    AnnualReportListPage,
    AnnualReportPage,
    BasicPage,
    ContactPage,
    FundingPage,
    HomePage,
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


class HomePageTests(WagtailPageTests):
    def test_homepage_child_page_types(self):
        """
        Verify allowed child page types.
        """
        self.assertAllowedSubpageTypes(
            HomePage,
            {
                ArticleLandingPage,
                ArticleListPage,
                ArticleSeriesListPage,
                ArticleSeriesPage,
                BasicPage,
                ContactPage,
                EventListPage,
                JobPostingListPage,
                MediaLandingPage,
                MultimediaListPage,
                MultimediaSeriesListPage,
                MultimediaSeriesPage,
                NewsletterListPage,
                PeoplePage,
                PersonListPage,
                PrivacyNoticePage,
                ProjectListPage,
                PublicationListPage,
                PublicationSeriesListPage,
                ResearchLandingPage,
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
