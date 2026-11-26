from datetime import datetime

from django.test import RequestFactory, TestCase
from django.utils import timezone

from home.models import HomePage
from multimedia.models import MultimediaListPage, MultimediaPage
from wagtail.models import Locale, Page

from .faceted_listing import build_listing_context


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
                publishing_date=timezone.make_aware(datetime(year, 1, index + 1)),
            ))
            if multimedia_type == 'audio':
                cls.audio_ids.add(page.pk)

    def context(self, params=None):
        request = RequestFactory().get('/', params or {})
        return build_listing_context(request, {
            'card_type': 'resource',
            'prefix': 'media',
            'show_filters': True,
            'show_search': True,
            'content_types': ['multimedia'],
        })

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

    def test_audio_and_year_filters_combine(self):
        context = self.context({'media-type': 'audio', 'media-year': '2024'})

        self.assertEqual(
            {page.pk for page in context['router_results']},
            self.audio_ids,
        )
