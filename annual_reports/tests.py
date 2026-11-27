import json
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import PropertyMock, patch

from core.models import BasicPage
from django.test import SimpleTestCase
from wagtail.test.utils import WagtailPageTestCase

from .models import (
    AnnualReportListPage,
    AnnualReportPage,
    AnnualReportSPAPage,
    AnnualReportSlidePage,
    MapStory,
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
    def test_map_stories_include_french_content_and_preserve_map_keys(self):
        story = MapStory(
            title="English title",
            title_fr="Titre français",
            short_description="<p>English description</p>",
            short_description_fr="<p>Description française</p>",
            location="Ottawa, Canada",
            location_fr="Ottawa, Canada français",
            research_theme_fr="Thème français",
            publishing_date=datetime(2026, 1, 15),
            latitude=45.4,
            longitude=-75.7,
            related_content=[("content", {
                "type": "video",
                "type_override": "English type",
                "type_override_fr": "Type français",
                "title_en": "<p>English link</p>",
                "title_fr": "<p>Lien français</p>",
                "link_override": "https://example.com/",
            })],
        )
        without_coordinates = MapStory(title="Missing", location="Unknown")
        slide = AnnualReportSlidePage(id=1, slide_type="map")
        items = [SimpleNamespace(story=story), SimpleNamespace(story=without_coordinates)]

        with patch.object(AnnualReportSlidePage, "map_stories", new_callable=PropertyMock) as manager:
            manager.return_value.all.return_value = items
            stories = slide.get_annual_report_slide_content()["map_stories"]

        self.assertEqual(len(stories), 1)
        result = stories[0]
        self.assertEqual(result["title"], "English title")
        self.assertEqual(result["title_fr"], "Titre français")
        self.assertEqual(result["short_description_fr"], "<p>Description française</p>")
        self.assertEqual(result["location"], "Ottawa, Canada")
        self.assertEqual(result["location_fr"], "Ottawa, Canada français")
        self.assertEqual(result["country"], "Canada")
        self.assertEqual(result["research_theme_fr"], "Thème français")
        self.assertEqual(result["publishing_date_iso"], "2026-01-15")
        related = result["related_pages"][0]
        self.assertEqual(related["title"], "English link")
        self.assertEqual(related["title_fr"], "Lien français")
        self.assertEqual(related["content_type_fr"], "Vidéo")
        self.assertEqual(related["type_override_fr"], "Type français")

    def test_map_story_french_fields_are_optional(self):
        story = MapStory(title="English", location="Paris, France", latitude=48.8, longitude=2.3)
        slide = AnnualReportSlidePage(id=1, slide_type="map")
        with patch.object(AnnualReportSlidePage, "map_stories", new_callable=PropertyMock) as manager:
            manager.return_value.all.return_value = [SimpleNamespace(story=story)]
            result = slide.get_annual_report_slide_content()["map_stories"][0]

        self.assertEqual(result["title_fr"], "")
        self.assertEqual(result["short_description_fr"], "")
        self.assertEqual(result["location_fr"], "")
        self.assertEqual(result["research_theme_fr"], "")
        self.assertEqual(result["publishing_date_iso"], "")

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
