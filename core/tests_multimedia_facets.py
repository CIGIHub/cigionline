from datetime import datetime

from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase
from django.utils import timezone

from home.models import HomePage
from multimedia.models import MultimediaListPage, MultimediaPage
from streams.blocks import FacetedListingBlock
from wagtail.models import Locale, Page

from .faceted_listing import FACETS_BY_CARD_TYPE, build_listing_context


class MultimediaFacetedListingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Locale.objects.get_or_create(language_code='en')
        root = Page.objects.first() or Page.add_root(instance=Page(
            title='Root', slug='root'))
        home = HomePage.objects.first() or root.add_child(instance=HomePage(
            title='Home', slug='home'))
        listing = home.add_child(instance=MultimediaListPage(
            title='Multimedia facet listing', slug='multimedia-facet-listing'))
        cls.audio_ids = set()
        for index in range(10):
            multimedia_type = 'audio' if index < 5 else 'video'
            year = 2024 if multimedia_type == 'audio' else 2025
            page = listing.add_child(instance=MultimediaPage(
                title='Multimedia facet %d' % index,
                slug='multimedia-facet-%d' % index,
                multimedia_type=multimedia_type,
                podcast_audio_duration='42:15' if multimedia_type == 'audio' else '',
                podcast_subtitle='Audio subtitle' if multimedia_type == 'audio' else '',
                publishing_date=timezone.make_aware(datetime(year, 1, index + 1)),
            ))
            if multimedia_type == 'audio':
                cls.audio_ids.add(page.pk)
                cls.audio = page

    def context(self, params=None):
        request = RequestFactory().get('/', params or {})
        return build_listing_context(request, {
            'card_type': 'multimedia',
            'prefix': 'media',
            'show_filters': True,
            'show_search': True,
            'facets': ['topic', 'type', 'year'],
        })

    def test_multimedia_card_type_is_available_to_editors(self):
        self.assertIn(('multimedia', 'Multimedia'), FacetedListingBlock.CARD_TYPES)
        self.assertEqual(
            FACETS_BY_CARD_TYPE['multimedia'],
            ('topic', 'type', 'year'),
        )

    def test_multimedia_scope_builds_audio_video_topic_and_year_facets(self):
        context = self.context()

        self.assertEqual(
            [facet['key'] for facet in context['router_facets']],
            ['topic', 'type', 'year'],
        )
        self.assertEqual(
            [option['label'] for option in context['router_facets'][1]['options']],
            ['Audio', 'Video'],
        )
        self.assertEqual(
            context['router_results_template'],
            'includes/router_items/multimedia.html',
        )

    def test_audio_and_year_filters_combine(self):
        context = self.context({'media-type': 'audio', 'media-year': '2024'})

        self.assertEqual(
            {page.pk for page in context['router_results']},
            self.audio_ids,
        )

    def test_multimedia_card_shows_medium_subtitle_date_and_duration(self):
        html = render_to_string(
            'includes/router_items/multimedia.html',
            {'item': self.audio},
        )

        self.assertIn('Audio', html)
        self.assertIn('Audio subtitle', html)
        self.assertIn('January 5, 2024', html)
        self.assertIn('42:15', html)
