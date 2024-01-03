
from distutils.log import error
from django.db import models
from django.utils import timezone
from events.models import EventPage, EventListPage
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from .blocks import (
    FeaturedExpertBlock,
    FeaturedPageBlock,
    FeaturedPublicationBlock,
    FeaturedMultimediaBlock,
    FeaturedHighlightBlock,
    FeaturedEventBlock,
    FeaturedPromotionBlock,
)
import traceback


class FeaturesListPage(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = [
        'features.HomePageFeaturedPromotionsList',
        'features.HomePageFeaturedContentList',
        'features.HomePageFeaturedPublicationsList',
        'features.HomePageFeaturedExpertsList',
        'features.HomePageFeaturedMultimediaList',
        'features.HomePageFeaturedHighlightsList',
        'features.HomePageFeaturedEventsList',
    ]
    max_count = 1

    class Meta:
        verbose_name = 'Feature List Page'


class HomePageFeaturedPromotionsList(Page):
    featured_promotions = StreamField(
        [
            ('featured_promotion', FeaturedPromotionBlock()),
        ],
        blank=True,
        use_json_field=True,
    )
    content_panels = Page.content_panels + [
        FieldPanel('featured_promotions'),
    ]
    parent_page_types = ['features.FeaturesListPage']
    subpage_types = []
    max_count = 1

    def __str__(self):
        return 'Home Page Ad blocks List'

    class Meta:
        verbose_name = 'Home Page Featured Promotions List'


class HomePageFeaturedContentList(Page):
    featured_pages = StreamField(
        [
            ('featured_page', FeaturedPageBlock()),
        ],
        blank=True,
        help_text='1: large | 2-4: medium | 5-9: small',
        use_json_field=True,
    )
    content_panels = Page.content_panels + [
        FieldPanel('featured_pages'),
    ]
    parent_page_types = ['features.FeaturesListPage']
    subpage_types = []
    max_count = 1

    def __str__(self):
        return 'Home Page Main Features List'

    class Meta:
        verbose_name = 'Home Page Main Features List'


class HomePageFeaturedPublicationsList(Page):
    featured_publications = StreamField(
        [
            ('featured_publication', FeaturedPublicationBlock()),
        ],
        blank=True,
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('featured_publications'),
    ]

    parent_page_types = ['features.FeaturesListPage']
    subpage_types = []
    max_count = 1

    def __str__(self):
        return 'Home Page Featured Publications List'


class HomePageFeaturedHighlightsList(Page):
    featured_highlights = StreamField(
        [
            ('featured_highlight', FeaturedHighlightBlock()),
        ],
        blank=True,
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('featured_highlights'),
    ]

    parent_page_types = ['features.FeaturesListPage']
    subpage_types = []
    max_count = 1

    def __str__(self):
        return 'Home Page Featured Highlights List'


class HomePageFeaturedMultimediaList(Page):
    featured_multimedia = StreamField(
        [
            ('featured_multimedia', FeaturedMultimediaBlock()),
        ],
        blank=True,
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('featured_multimedia'),
    ]

    parent_page_types = ['features.FeaturesListPage']
    subpage_types = []
    max_count = 1

    def __str__(self):
        return 'Home Page Featured Multimedia List'


class HomePageFeaturedEventsList(Page):
    featured_events = StreamField(
        [
            ('featured_event', FeaturedEventBlock()),
        ],
        blank=True,
        use_json_field=True,
        help_text='Use this list only if you want to feature different events than those featured on the Events Landing Page.',
    )

    content_panels = Page.content_panels + [
        FieldPanel('featured_events'),
    ]

    parent_page_types = ['features.FeaturesListPage']
    subpage_types = []
    max_count = 1

    def __str__(self):
        return 'Home Page Featured Events List'

    def get_context(self, request):
        context = super().get_context(request)

        featured_events = []
        try:
            featured_events_query_set = self.featured_events
            featured_event_ids = [event.value['page'].id for event in featured_events_query_set]
            featured_events = EventPage.objects.prefetch_related(
                'authors__author',
                'topics',
            ).in_bulk(featured_event_ids)
            featured_events = [featured_events[x] for x in featured_events]
        except Exception:
            error(traceback.format_exc())

        if len(featured_events) == 0:
            featured_events = EventListPage.objects.first().get_featured_events()[:3]
            if not featured_events:
                now = timezone.now()
                future_events = EventPage.objects.prefetch_related(
                    'multimedia_page',
                    'topics',
                ).live().public().filter(publishing_date__gt=now).order_by('publishing_date')[:3]
                if len(future_events) < 3:
                    Q = models.Q
                    past_events = EventPage.objects.prefetch_related(
                        'multimedia_page',
                        'topics',
                    ).live().public().filter(Q(event_end__isnull=True, publishing_date__lt=now) | Q(event_end__lt=now)).order_by('-publishing_date')[:3]
                    featured_events = (list(future_events) + list(past_events))[:3]
                else:
                    featured_events = future_events

        context['featured_events'] = featured_events
        return context


class HomePageFeaturedExpertsList(Page):
    featured_experts = StreamField(
        [
            ('featured_expert', FeaturedExpertBlock()),
        ],
        blank=True,
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('featured_experts'),
    ]

    parent_page_types = ['features.FeaturesListPage']
    subpage_types = []
    max_count = 1

    def __str__(self):
        return 'Home Page Featured Experts List'
