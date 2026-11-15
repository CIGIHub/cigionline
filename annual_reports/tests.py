from unittest.mock import patch

from core.models import BasicPage
from django.core.cache import cache
from django.test import SimpleTestCase, override_settings
from geopy.exc import GeocoderServiceError
from wagtail.test.utils import WagtailPageTestCase

from .models import (
    AnnualReportListPage,
    AnnualReportPage,
    AnnualReportSPAPage,
    MapStory,
)


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


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'annual-report-map-tests',
    },
})
class MapStoryTests(SimpleTestCase):
    def tearDown(self):
        cache.clear()

    @patch('annual_reports.models.Nominatim')
    def test_coordinates_are_cached(self, nominatim):
        nominatim.return_value.geocode.return_value.latitude = 43.46
        nominatim.return_value.geocode.return_value.longitude = -80.52
        story = MapStory(location='Waterloo, Canada')

        expected = {'latitude': 43.46, 'longitude': -80.52}
        self.assertEqual(story.coordinates, expected)
        self.assertEqual(story.coordinates, expected)
        nominatim.return_value.geocode.assert_called_once_with('Waterloo, Canada')

    @patch('annual_reports.models.Nominatim')
    def test_coordinates_ignore_geocoder_outage(self, nominatim):
        nominatim.return_value.geocode.side_effect = GeocoderServiceError('offline')

        self.assertIsNone(MapStory(location='Waterloo, Canada').coordinates)
