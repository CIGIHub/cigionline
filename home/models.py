from distutils.log import error
from django.db import models
from modelcluster.fields import ParentalKey
from publications.models import PublicationPage, PublicationListPage
from research.models import ProjectPage, ProjectListPage
from events.models import EventPage, EventListPage
from features.models import (
    HomePageFeaturedPromotionsList,
    HomePageFeaturedContentList,
    HomePageFeaturedPublicationsList,
    HomePageFeaturedExpertsList,
    HomePageFeaturedMultimediaList,
    HomePageFeaturedHighlightsList,
    HomePageFeaturedEventsList,
)
from streams.blocks import ParagraphBlock, PersonsListBlock
from wagtail.admin.panels import (
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    FieldPanel
)
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from django.utils import timezone
from people.models import PersonPage
from multimedia.models import MultimediaPage
import random
import traceback


class HomePage(Page):
    """Singleton model for the home page."""

    banner_text = RichTextField(
        blank=True,
        null=True,
        verbose_name='Banner Text',
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel(
                    'banner_text',
                ),
            ],
            heading='Banner',
            classname='collapsible collapsed',
        ),
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
            help_text='1: large | 2-4: medium | 5-9: small'
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
                    max_num=4,
                    min_num=0,
                    label='Promotion Block',
                ),
            ],
            heading='Promotion Blocks',
            classname='collapsible collapsed',
        ),
    ]

    def get_featured_pages(self):
        try:
            featured_pages_list = HomePageFeaturedContentList.objects.first().featured_pages
            featured_page_ids = [page.value['page'].id for page in featured_pages_list]
        except Exception:
            error(traceback.format_exc())
            featured_page_ids = self.featured_pages.order_by('sort_order').values_list('featured_page', flat=True)
        pages = Page.objects.specific().in_bulk(featured_page_ids)
        return [pages[x] for x in featured_page_ids]

    def get_featured_experts(self):
        try:
            featured_experts = HomePageFeaturedExpertsList.objects.first().featured_experts
            featured_expert_ids = [expert.value['page'].id for expert in featured_experts]
        except Exception:
            error(traceback.format_exc())
            featured_expert_ids = self.featured_experts.values_list('featured_expert', flat=True)

        experts = PersonPage.objects.in_bulk(featured_expert_ids)
        return [experts[x] for x in featured_expert_ids]

    def get_featured_experts_list(self):
        featured_experts = self.get_featured_experts()
        exclude_ids = [expert.id for expert in featured_experts]

        additional_experts_id_list = list(PersonPage.objects.live().public().filter(
            person_types__name='Expert',
            archive=0
        ).exclude(id__in=exclude_ids).distinct().values_list('id', flat=True))
        random_additional_experts_id_list = random.sample(additional_experts_id_list, min(len(additional_experts_id_list), 3))
        featured_experts = list(featured_experts) + list(PersonPage.objects.filter(id__in=random_additional_experts_id_list))[:3 - len(featured_experts)]

        return featured_experts

    def get_highlight_pages(self):
        try:
            highlight_pages = HomePageFeaturedHighlightsList.objects.first().featured_highlights
            highlight_page_ids = [page.value['page'].id for page in highlight_pages]
        except Exception:
            error(traceback.format_exc())
            highlight_page_ids = self.highlight_pages.values_list('highlight_page', flat=True)

        pages = Page.objects.specific().prefetch_related(
            'authors__author',
            'topics',
        ).in_bulk(highlight_page_ids)
        return [pages[x] for x in highlight_page_ids]

    def get_featured_multimedia(self):
        try:
            featured_multimedia = HomePageFeaturedMultimediaList.objects.first().featured_multimedia
            featured_multimedia_ids = [multimedia.value['page'].id for multimedia in featured_multimedia]
        except Exception:
            error(traceback.format_exc())
            featured_multimedia_ids = self.featured_multimedia.values_list('featured_multimedia', flat=True)

        multimedia = MultimediaPage.objects.prefetch_related(
            'authors__author',
            'topics',
        ).in_bulk(featured_multimedia_ids)
        return [multimedia[x] for x in featured_multimedia_ids]

    def get_featured_publications(self):
        featured_publications = []
        try:
            featured_publications_list = HomePageFeaturedPublicationsList.objects.first().featured_publications
            featured_publication_ids = [publication.value['page'].id for publication in featured_publications_list]
            featured_publications_query_set = PublicationPage.objects.prefetch_related(
                'authors__author',
                'topics',
            ).in_bulk(featured_publication_ids)
            featured_publications = [featured_publications_query_set[x] for x in featured_publication_ids]
        except Exception:
            error(traceback.format_exc())

        if len(featured_publications) == 0:
            featured_page_ids = []
            try:
                featured_pages_list = HomePageFeaturedContentList.objects.first().featured_pages
                featured_page_ids = [page.value['page'].id for page in featured_pages_list]
            except Exception:
                error(traceback.format_exc())
                featured_page_ids = self.featured_pages.values_list('featured_page', flat=True)
            featured_publications = PublicationPage.objects.prefetch_related(
                'authors__author',
                'topics',
            ).live().public().exclude(id__in=featured_page_ids).exclude(publication_type__title='Working Paper').order_by('-publishing_date')[:4]

        return featured_publications

    def get_featured_events(self):
        featured_events = []
        try:
            featured_events_query_set = HomePageFeaturedEventsList.objects.first().featured_events
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

        return featured_events

    def get_promotion_blocks(self):
        promotion_blocks = [block.value['block'] for block in HomePageFeaturedPromotionsList.objects.first().featured_promotions]

        return promotion_blocks

    def featured_content_revision_created_at(self):
        try:
            return HomePageFeaturedContentList.objects.first().last_published_at
        except Exception:
            return ''

    def featured_publications_revision_created_at(self):
        try:
            return f'{HomePageFeaturedPublicationsList.objects.first().last_published_at}{HomePageFeaturedContentList.objects.first().last_published_at}'
        except Exception:
            return ''

    def featured_events_revision_created_at(self):
        try:
            return HomePageFeaturedEventsList.objects.first().last_published_at
        except Exception:
            return ''

    def featured_promotions_revision_created_at(self):
        try:
            return HomePageFeaturedPromotionsList.objects.first().last_published_at
        except Exception:
            return ''

    def featured_highlights_revision_created_at(self):
        try:
            return HomePageFeaturedHighlightsList.objects.first().last_published_at
        except Exception:
            return ''

    def featured_multimedia_revision_created_at(self):
        try:
            return HomePageFeaturedMultimediaList.objects.first().last_published_at
        except Exception:
            return ''

    def featured_experts_revision_created_at(self):
        try:
            return HomePageFeaturedExpertsList.objects.first().last_published_at
        except Exception:
            return ''

    def get_context(self, request):
        context = super().get_context(request)
        context['featured_pages'] = self.get_featured_pages()
        context['featured_experts'] = self.get_featured_experts_list()
        context['highlight_pages'] = self.get_highlight_pages()
        context['featured_multimedia'] = self.get_featured_multimedia()
        context['featured_publications'] = self.get_featured_publications()
        context['featured_events'] = self.get_featured_events()
        context['promotion_blocks'] = self.get_promotion_blocks()
        return context

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
        'features.FeaturesListPage',
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
        'research.TopicListPage',
        'subscribe.SubscribePage',
    ]
    templates = 'core/home_page.html'

    class Meta:
        verbose_name = 'Home Page'

class Think7HomePage(Page):
    """Singleton model for the Think 7 Canada home page."""
    
    body = StreamField(
        [
            ('paragraph', ParagraphBlock()),
        ],
        blank=True,
    )
    
    board_members = StreamField(
        [
            ('board_members', PersonsListBlock()),
        ],
        blank=True,
    )
    
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('body'),
            ],
            heading='Body',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('board_members'),
            ],
            heading='Board Members',
            classname='collapsible collapsed',
        ),
    ]
    
    def get_task_forces(self):
        return self.get_children().type(ProjectListPage).first().get_children().type(ProjectPage).live().public()
    
    def get_latest_publication(self):
        return self.get_children().type(PublicationListPage).first().get_children().type(PublicationPage).live().public().first()
    
    def get_latest_event(self):
        return self.get_children().type(EventListPage).first().get_children().type(EventPage).live().public().first()
    
    max_count = 1
    subpage_types = [
        'articles.ArticleListPage',
        'contact.ContactPage',
        'core.BasicPage',
        'core.Think7AbstractPage',
        'events.EventListPage',
        'people.PeoplePage',
        'people.PersonListPage',
        'publications.PublicationListPage',
        'research.ProjectListPage',
    ]
    
    def get_template(self, request, *args, **kwargs):
        return 'think7/home_page.html'
    
    class Meta:
        verbose_name = 'Think 7 Home Page'

class HomePageFeaturedPage(Orderable):
    home_page = ParentalKey(
        'home.HomePage',
        related_name='featured_pages',
    )
    featured_page = models.ForeignKey(
        'core.ContentPage',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Content Page',
    )

    panels = [
        PageChooserPanel(
            'featured_page',
            ['core.ContentPage'],
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
        ),
    ]
