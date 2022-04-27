from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from modelcluster.fields import ParentalKey
from publications.models import PublicationPage
from events.models import EventPage, EventListPage
from features.models import HomePageFeaturedPromotionsPage
from wagtail.admin.edit_handlers import (
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    FieldPanel
)
from wagtail.core.models import Orderable, Page
from django.utils import timezone
from people.models import PersonPage
from multimedia.models import MultimediaPage
import random
import logging
import traceback


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
            help_text='1: large | 2-4: medium | 5-9: small'
        ),
        MultiFieldPanel(
            [
                InlinePanel(
                    'replacement_featured_pages',
                    max_num=9,
                    min_num=0,
                    label='Page',
                ),
            ],
            heading='Replacement Featured Content',
            classname='collapsible collapsed',
            help_text='1: large | 2-4: medium | 5-9: small; Use this section if items that need to be featured are not of Content Page type. Items in this list will replace items in the Featured Content.'
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
    ]

    def get_featured_pages(self):
        featured_page_ids = self.featured_pages.order_by('sort_order').values_list('featured_page', flat=True)
        pages = Page.objects.specific().prefetch_related(
            'authors__author',
            'topics',
        ).in_bulk(featured_page_ids)
        return [pages[x] for x in featured_page_ids]

    def get_replaced_feature_pages(self):
        featured_pages = self.get_featured_pages()
        replacement_featured_page_ids = self.replacement_featured_pages.order_by('sort_order').values_list('replacement_featured_page', 'position')
        pages = Page.objects.specific().in_bulk([i[0] for i in replacement_featured_page_ids])
        replacement_featured_pages = [pages[x[0]] for x in replacement_featured_page_ids]

        for i in range(len(replacement_featured_pages)):
            position = replacement_featured_page_ids[i][1] - 1
            if (len(featured_pages) > position):
                featured_pages[position] = replacement_featured_pages[i]
        return featured_pages

    def get_featured_experts(self):
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
        highlight_pages_ids = self.highlight_pages.values_list('highlight_page', flat=True)
        pages = Page.objects.specific().prefetch_related(
            'authors__author',
            'topics',
        ).in_bulk(highlight_pages_ids)
        return [pages[x] for x in highlight_pages_ids]

    def get_featured_multimedia(self):
        featured_multimedia_ids = self.featured_multimedia.values_list('featured_multimedia', flat=True)
        multimedia = MultimediaPage.objects.prefetch_related(
            'authors__author',
            'topics',
        ).in_bulk(featured_multimedia_ids)
        return [multimedia[x] for x in featured_multimedia_ids]

    def get_featured_publications(self):
        featured_items_ids = self.featured_pages.values_list('featured_page', flat=True)
        return PublicationPage.objects.prefetch_related(
            'authors__author',
            'topics',
        ).live().public().exclude(id__in=featured_items_ids).order_by('-publishing_date')[:4]

    def get_featured_events(self):
        try:
            featured_events = EventListPage.objects.first().get_featured_events()[:3]
        except Exception:
            logging.error(traceback.format_exc())
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

    def get_promotion_blocks(self):
        featured_promotions_page = HomePageFeaturedPromotionsPage.objects.first()
        promotion_blocks_list = []
        for item in featured_promotions_page.promotion_blocks.prefetch_related(
            'promotion_block',
        ).all():
            promotion_blocks_list.append(item.promotion_block)
        return promotion_blocks_list

    def get_context(self, request):
        context = super().get_context(request)
        context['featured_pages'] = self.get_replaced_feature_pages()
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


class HomePageReplacementFeaturedPage(Orderable):
    home_page = ParentalKey(
        'home.HomePage',
        related_name='replacement_featured_pages',
    )
    replacement_featured_page = models.ForeignKey(
        'wagtailcore.Page',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Page',
    )
    position = models.IntegerField(
        null=False,
        blank=False,
        help_text='Enter the position of the item that will be replaced',
        validators=[MinValueValidator(1), MaxValueValidator(9)]
    )

    panels = [
        PageChooserPanel(
            'replacement_featured_page',
            ['wagtailcore.Page'],
        ),
        FieldPanel('position'),
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
