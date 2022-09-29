from django.core.cache import cache
from wagtail.admin.edit_handlers import StreamFieldPanel, FieldPanel

from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from .blocks import (
    FeaturedExpertBlock,
    FeaturedPageBlock,
    FeaturedPublicationBlock,
    FeaturedMultimediaBlock,
    FeaturedHighlightBlock,
    FeaturedEventBlock,
    FeaturedPromotionBlock,
)


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
    )
    content_panels = Page.content_panels + [
        StreamFieldPanel('featured_promotions'),
    ]
    parent_page_types = ['features.FeaturesListPage']
    subpage_types = []
    max_count = 1

    def __str__(self):
        return 'Home Page Ad blocks List'

    def save(self, *args, **kwargs):
        cache.delete_pattern('*homepage_featured_promotions*')
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Home Page Featured Promotions List'


class HomePageFeaturedContentList(Page):
    featured_pages = StreamField(
        [
            ('featured_page', FeaturedPageBlock()),
        ],
        blank=True,
        help_text='1: large | 2-4: medium | 5-9: small'
    )
    content_panels = Page.content_panels + [
        StreamFieldPanel('featured_pages'),
    ]
    parent_page_types = ['features.FeaturesListPage']
    subpage_types = []
    max_count = 1

    def __str__(self):
        return 'Home Page Main Features List'

    def save(self, *args, **kwargs):
        cache.delete_pattern('*homepage_featured_content*')
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Home Page Main Features List'


class HomePageFeaturedPublicationsList(Page):
    featured_publications = StreamField(
        [
            ('featured_publication', FeaturedPublicationBlock()),
        ],
        blank=True,
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel('featured_publications'),
    ]

    parent_page_types = ['features.FeaturesListPage']
    subpage_types = []
    max_count = 1

    def __str__(self):
        return 'Home Page Featured Publications List'

    def save(self, *args, **kwargs):
        cache.delete_pattern('*homepage_featured_publications*')
        super().save(*args, **kwargs)


class HomePageFeaturedHighlightsList(Page):
    featured_highlights = StreamField(
        [
            ('featured_highlight', FeaturedHighlightBlock()),
        ],
        blank=True,
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel('featured_highlights'),
    ]

    parent_page_types = ['features.FeaturesListPage']
    subpage_types = []
    max_count = 1

    def __str__(self):
        return 'Home Page Featured Highlights List'

    def save(self, *args, **kwargs):
        cache.delete_pattern('*homepage_featured_highlights*')
        super().save(*args, **kwargs)


class HomePageFeaturedMultimediaList(Page):
    featured_multimedia = StreamField(
        [
            ('featured_multimedia', FeaturedMultimediaBlock()),
        ],
        blank=True,
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel('featured_multimedia'),
    ]

    parent_page_types = ['features.FeaturesListPage']
    subpage_types = []
    max_count = 1

    def __str__(self):
        return 'Home Page Featured Multimedia List'

    def save(self, *args, **kwargs):
        cache.delete_pattern('*homepage_featured_multimedia*')
        super().save(*args, **kwargs)


class HomePageFeaturedEventsList(Page):
    featured_events = StreamField(
        [
            ('featured_event', FeaturedEventBlock()),
        ],
        blank=True,
        help_text='Use this list only if you want to feature different events than those featured on the Events Landing Page.',
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel('featured_events'),
    ]

    parent_page_types = ['features.FeaturesListPage']
    subpage_types = []
    max_count = 1

    def __str__(self):
        return 'Home Page Featured Events List'

    def save(self, *args, **kwargs):
        cache.delete_pattern('*homepage_featured_events*')
        super().save(*args, **kwargs)


class HomePageFeaturedExpertsList(Page):
    featured_experts = StreamField(
        [
            ('featured_expert', FeaturedExpertBlock()),
        ],
        blank=True,
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel('featured_experts'),
    ]

    parent_page_types = ['features.FeaturesListPage']
    subpage_types = []
    max_count = 1

    def __str__(self):
        return 'Home Page Featured Experts List'

    def save(self, *args, **kwargs):
        cache.delete_pattern('*homepage_featured_experts*')
        super().save(*args, **kwargs)
