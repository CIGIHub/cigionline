import json
from types import SimpleNamespace
from unittest.mock import patch

from core.models import BasicPage
from django.test import SimpleTestCase
from wagtail.test.utils import WagtailPageTestCase

from .models import (
    AnnualReportListPage,
    AnnualReportPage,
    AnnualReportSPAPage,
    AnnualReportSlidePage,
)
from .views import get_ordered_slides_annual_report


class AnnualReportListPageTests(WagtailPageTestCase):
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


class AnnualReportPageTests(WagtailPageTestCase):
    def test_annualreportpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            AnnualReportPage,
            {AnnualReportListPage},
        )

    def test_annualreportpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            AnnualReportPage,
            {AnnualReportSPAPage},
        )


class AnnualReportSlidesAPITests(SimpleTestCase):
    def test_background_quote_gradient_can_be_disabled(self):
        slide = AnnualReportSlidePage(
            id=2,
            title="Test slide",
            slug="test-slide",
            slide_title="Test slide",
            slide_title_fr="Diapositive de test",
            slide_type="standard",
            background_colour="black",
            background_quote="A quote",
            background_quote_fr="Une citation",
            background_quote_position="top-right",
            ar_slide_content=[],
        )
        page = AnnualReportSPAPage(
            id=1,
            title="Test report",
            year=2026,
            slides=[("slide", {"slide": slide})],
        )

        with (
            patch(
                "annual_reports.views.get_object_or_404",
                return_value=SimpleNamespace(specific=page),
            ),
            patch("annual_reports.views.AnnualReportSlidePage.objects.filter", return_value=[slide]),
        ):
            default_response = get_ordered_slides_annual_report(None, page.id)
            slide.show_background_quote_gradient = False
            disabled_response = get_ordered_slides_annual_report(None, page.id)

        default_slide = json.loads(default_response.content)["slides"][0]
        disabled_slide = json.loads(disabled_response.content)["slides"][0]
        self.assertEqual(default_slide["background_gradient_position"], "right")
        self.assertEqual(disabled_slide["background_gradient_position"], "none")

    def test_fund_balances_include_donations(self):
        slide = AnnualReportSlidePage(
            id=3,
            slide_type="financials",
            ar_slide_content=[
                (
                    "fund_balances",
                    {
                        "amounts": {
                            "year_current": {"donations": "1,000"},
                            "year_previous": {"donations": "500"},
                        },
                    },
                ),
            ],
        )

        fund_balances = slide.get_annual_report_slide_content()["tabs"][0]

        self.assertEqual(fund_balances["year_current"]["donations"], "1,000")
        self.assertEqual(fund_balances["year_previous"]["donations"], "500")
