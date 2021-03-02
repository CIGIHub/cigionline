from django.db import models
from modelcluster.fields import ParentalKey
from publications.models import PublicationPage
from events.models import EventPage
from wagtail.admin.edit_handlers import (
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    FieldPanel
)
from wagtail.core.models import Orderable, Page
from django.utils import timezone


class HomePage(Page):
    """Singleton model for the home page."""

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                InlinePanel(
                    'featured_pages',
                    max_num=9,
                    min_num=0,
                    label='Page',
                ),
            ],
            heading='Featured Content',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                InlinePanel(
                    'highlight_pages',
                    max_num=12,
                    min_num=0,
                    label='Page',
                ),
            ],
            heading='Highlights',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                InlinePanel(
                    'featured_multimedia',
                    max_num=12,
                    min_num=0,
                    label='Multimedia',
                ),
            ],
            heading='Featured Multimedia',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                InlinePanel(
                    'featured_experts',
                    max_num=3,
                    min_num=0,
                    label='Expert',
                ),
            ],
            heading='Featured Experts',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                InlinePanel(
                    'promotion_blocks',
                    max_num=2,
                    min_num=0,
                    label='Promotion Block',
                ),
            ],
            heading='Promotion Blocks',
            classname='collapsible collapsed',
        ),
    ]

    def featured_large(self):
        first_featured = self.featured_pages.prefetch_related(
            'featured_page',
        ).first()
        if first_featured:
            return first_featured.featured_page.specific
        return False

    def featured_medium(self):
        featured_medium = []
        featured_medium_query = self.featured_pages.prefetch_related(
            'featured_page',
        ).all()[1:4]
        for item in featured_medium_query:
            featured_medium.append(item.featured_page.specific)
        return featured_medium

    def featured_small(self):
        featured_small = []
        featured_small_query = self.featured_pages.prefetch_related(
            'featured_page',
        ).all()[4:]
        for item in featured_small_query:
            featured_small.append(item.featured_page.specific)
        return featured_small

    def featured_publications(self):
        return PublicationPage.objects.prefetch_related(
            # 'authors__author',
            'topics',
        ).live().public().order_by('-publishing_date')[:4]

    def featured_multimedia_large(self):
        first_featured_multimedia = self.featured_multimedia.prefetch_related(
            # 'featured_multimedia__authors__author',
            'featured_multimedia__topics',
        ).first()
        if first_featured_multimedia:
            return first_featured_multimedia.featured_multimedia
        return False

    def featured_multimedia_small(self):
        featured_multimedia_small = []
        for item in self.featured_multimedia.prefetch_related(
            # 'featured_multimedia__authors__author',
            'featured_multimedia__topics',
        ).all()[1:]:
            featured_multimedia_small.append(item.featured_multimedia)
        return featured_multimedia_small

    def featured_experts_list(self):
        featured_experts = []
        for item in self.featured_experts.prefetch_related(
            'featured_expert',
        ).all()[:3]:
            featured_experts.append(item.featured_expert)
        return featured_experts

    def promotion_blocks_list(self):
        promotion_blocks_list = []
        for item in self.promotion_blocks.prefetch_related(
            'promotion_block',
        ).all()[:2]:
            promotion_blocks_list.append(item.promotion_block)
        return promotion_blocks_list

    def featured_events(self):
        featured_events = []
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
        return featured_events

    max_count = 1
    subpage_types = [
        'articles.ArticleLandingPage',
        'articles.ArticleListPage',
        'articles.ArticleSeriesListPage',
        'articles.ArticleSeriesPage',
        'articles.MediaLandingPage',
        'careers.JobPostingListPage',
        'contact.ContactPage',
        'core.BasicPage',
        'core.PrivacyNoticePage',
        'events.EventListPage',
        'multimedia.MultimediaListPage',
        'multimedia.MultimediaSeriesListPage',
        'multimedia.MultimediaSeriesPage',
        'newsletters.NewsletterListPage',
        'people.PeoplePage',
        'people.PersonListPage',
        'publications.PublicationListPage',
        'publications.PublicationSeriesListPage',
        'research.ProjectListPage',
        'research.ResearchLandingPage',
        'research.TopicListPage'
    ]
    templates = 'core/home_page.html'

    class Meta:
        verbose_name = 'Home Page'


class HomePageFeaturedPage(Orderable):
    home_page = ParentalKey(
        'home.HomePage',
        related_name='featured_pages',
    )
    featured_page = models.ForeignKey(
        'wagtailcore.Page',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Page',
    )

    panels = [
        PageChooserPanel(
            'featured_page',
            ['wagtailcore.Page'],
        ),
    ]


class HomePageHighlightPage(Orderable):
    home_page = ParentalKey(
        'home.HomePage',
        related_name='highlight_pages',
    )
    highlight_page = models.ForeignKey(
        'wagtailcore.Page',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Highlight',
    )

    panels = [
        PageChooserPanel(
            'highlight_page',
            ['articles.ArticleSeriesPage', 'publications.PublicationPage'],
        ),
    ]


class HomePageFeaturedExperts(Orderable):
    home_page = ParentalKey(
        'home.HomePage',
        related_name='featured_experts',
    )
    featured_expert = models.ForeignKey(
        'people.PersonPage',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Expert',
    )

    panels = [
        PageChooserPanel(
            'featured_expert',
            ['people.PersonPage'],
        ),
    ]


class HomePageFeaturedMultimedia(Orderable):
    home_page = ParentalKey(
        'home.HomePage',
        related_name='featured_multimedia',
    )
    featured_multimedia = models.ForeignKey(
        'multimedia.MultimediaPage',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Multimedia',
    )

    panels = [
        PageChooserPanel(
            'featured_multimedia',
            ['multimedia.MultimediaPage'],
        ),
    ]


class HomePagePromotionBlocks(Orderable):
    home_page = ParentalKey(
        'home.HomePage',
        related_name='promotion_blocks',
    )
    promotion_block = models.ForeignKey(
        'promotions.PromotionBlock',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Promotion Block',
    )

    panels = [
        FieldPanel(
            'promotion_block',
            ['promotions.PromotionBlock'],
        ),
    ]
