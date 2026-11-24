import json
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from core.models import BasicPage
from django.core.cache import cache
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase, override_settings
from geopy.exc import GeopyError
from streams.blocks import ARSlideContentBlock
from wagtail.test.utils import WagtailPageTestCase

from .models import (
    AnnualReportListPage,
    AnnualReportPage,
    AnnualReportSPAPage,
    AnnualReportSlidePage,
    MapStory,
    _geocode_cache_key,
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


class AnnualReportContentTypeTests(SimpleTestCase):
    def test_report_and_submission_are_available(self):
        choices = dict(ARSlideContentBlock().child_blocks['type'].field.choices)

        self.assertEqual(choices['report'], 'Report')
        self.assertEqual(choices['submission'], 'Submission')


class AnnualReportSlidesAPITests(SimpleTestCase):
    def test_background_quote_gradient_can_be_disabled(self):
        slide = AnnualReportSlidePage(
            id=2,
            title='Test slide',
            slug='test-slide',
            slide_title='Test slide',
            slide_title_fr='Diapositive de test',
            slide_type='standard',
            background_colour='black',
            background_quote='A quote',
            background_quote_fr='Une citation',
            background_quote_position='top-right',
            ar_slide_content=[],
        )
        page = AnnualReportSPAPage(
            id=1,
            title='Test report',
            year=2026,
            slides=[('slide', {'slide': slide})],
        )

        with (
            patch(
                'annual_reports.views.get_object_or_404',
                return_value=SimpleNamespace(specific=page),
            ),
            patch('annual_reports.views.AnnualReportSlidePage.objects.filter', return_value=[slide]),
        ):
            default_response = get_ordered_slides_annual_report(None, page.id)
            slide.show_background_quote_gradient = False
            disabled_response = get_ordered_slides_annual_report(None, page.id)

        default_slide = json.loads(default_response.content)['slides'][0]
        disabled_slide = json.loads(disabled_response.content)['slides'][0]
        self.assertEqual(default_slide['background_gradient_position'], 'right')
        self.assertEqual(disabled_slide['background_gradient_position'], 'none')

    def test_fund_balances_include_donations(self):
        slide = AnnualReportSlidePage(
            id=3,
            slide_type='financials',
            ar_slide_content=[
                (
                    'fund_balances',
                    {
                        'amounts': {
                            'year_current': {'donations': '1,000'},
                            'year_previous': {'donations': '500'},
                        },
                    },
                ),
            ],
        )

        fund_balances = slide.get_annual_report_slide_content()['tabs'][0]

        self.assertEqual(fund_balances['year_current']['donations'], '1,000')
        self.assertEqual(fund_balances['year_previous']['donations'], '500')

@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'annual-report-map-tests',
    },
})
class MapStoryTests(TestCase):
    def tearDown(self):
        cache.clear()

    @patch('annual_reports.models.Nominatim')
    def test_coordinates_are_stored(self, nominatim):
        nominatim.return_value.geocode.return_value.latitude = 43.46
        nominatim.return_value.geocode.return_value.longitude = -80.52
        story = MapStory.objects.create(title='Waterloo', location='Waterloo, Canada')

        expected = {'latitude': 43.46, 'longitude': -80.52}
        self.assertEqual(story.coordinates, expected)
        story.save()
        self.assertEqual(story.coordinates, expected)
        nominatim.return_value.geocode.assert_called_once_with('Waterloo, Canada')

    @patch('annual_reports.models.Nominatim')
    def test_coordinates_ignore_geocoder_outage(self, nominatim):
        nominatim.return_value.geocode.side_effect = GeopyError('offline')

        story = MapStory.objects.create(title='Waterloo', location='Waterloo, Canada')

        self.assertIsNone(story.coordinates)

    @patch('annual_reports.models.Nominatim')
    def test_coordinates_reuse_safe_cache_key(self, nominatim):
        cache.set(
            _geocode_cache_key('location', 'Waterloo, Canada'),
            {'latitude': 43.46, 'longitude': -80.52},
        )

        story = MapStory.objects.create(title='Waterloo', location='Waterloo, Canada')

        self.assertEqual(story.coordinates, {'latitude': 43.46, 'longitude': -80.52})
        nominatim.assert_not_called()

    @patch('annual_reports.models.cache.add', return_value=False)
    @patch('annual_reports.management.commands.backfill_map_coordinates.Nominatim')
    def test_backfill_uses_cached_coordinates(self, nominatim, cache_add):
        story = MapStory.objects.create(title='Waterloo', location='Waterloo, Canada')
        cache.set(
            _geocode_cache_key('location', story.location),
            {'latitude': 43.46, 'longitude': -80.52},
        )

        call_command('backfill_map_coordinates', stdout=StringIO())
        story.refresh_from_db()

        self.assertEqual(story.coordinates, {'latitude': 43.46, 'longitude': -80.52})
        nominatim.return_value.geocode.assert_not_called()
