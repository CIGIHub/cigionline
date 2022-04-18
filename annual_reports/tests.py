from core.models import BasicPage
from wagtail.tests.utils import WagtailPageTests

from .models import (
    AnnualReportListPage,
    AnnualReportPage, SummarySlidePage, ContentSlidePage, MessageSlidePage, OutputsAndActivitiesSlidePage,
    TimelineSlidePage, TabbedSlidePage,
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
            {
                SummarySlidePage,
                MessageSlidePage,
                ContentSlidePage,
                OutputsAndActivitiesSlidePage,
                TimelineSlidePage,
                TabbedSlidePage,
            },
        )
