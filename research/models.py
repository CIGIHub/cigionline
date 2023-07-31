from core.models import (
    ArchiveablePageAbstract,
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    SearchablePageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
)
from django.db import models
from django.db.models import Count
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from people.models import PersonPage
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.blocks import (
    CharBlock,
    PageChooserBlock,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.search import index
from streams.blocks import IgcTimelineBlock, PublicationCard, HomePageRow


class ProjectListPage(Page):
    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = ['research.ProjectPage']
    templates = 'research/project_list_page.html'

    class Meta:
        verbose_name = 'Activity List Page'


class ProjectPage(
    ArchiveablePageAbstract,
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
):
    body = StreamField(
        BasicPageAbstract.body_default_blocks + [
            BasicPageAbstract.body_poster_block,
            BasicPageAbstract.body_recommended_block,
            BasicPageAbstract.body_text_border_block,
        ],
        blank=True,
        use_json_field=True,
    )
    image_banner = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner Image',
    )
    layout = StreamField([
        ('row', HomePageRow()),
    ],
        blank=True,
    )
    project_contacts = StreamField(
        [
            ('contact', PageChooserBlock(required=True, page_type='people.PersonPage')),
        ],
        blank=True,
        use_json_field=True,
    )
    project_leads = StreamField(
        [
            ('project_lead', PageChooserBlock(required=True, page_type='people.PersonPage')),
            ('external_project_lead', CharBlock(required=True)),
        ],
        blank=True,
        use_json_field=True,
    )
    project_members = StreamField(
        [
            ('project_member', PageChooserBlock(required=True, page_type='people.PersonPage')),
            ('external_project_member', CharBlock(required=True)),
        ],
        blank=True,
        use_json_field=True,
    )
    project_types = ParentalManyToManyField('research.ProjectType', blank=True)
    related_files = StreamField(
        [
            ('file', DocumentChooserBlock()),
        ],
        blank=True,
        use_json_field=True,
    )

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        MultiFieldPanel([
            FieldPanel('layout'),
        ], heading='Layout', classname='collapsible collapsed home-page-layout'),
        MultiFieldPanel(
            [
                FieldPanel('publishing_date'),
                FieldPanel('project_types'),
            ],
            heading='General Information',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('project_leads'),
                FieldPanel('project_members'),
                FieldPanel('project_contacts'),
            ],
            heading='People',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('image_hero'),
                FieldPanel('image_banner'),
            ],
            heading='Images',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('topics'),
                FieldPanel('issues'),
                FieldPanel('related_files'),
            ],
            heading='Related',
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
        ),
    ]

    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        ShareablePageAbstract.social_panel,
        SearchablePageAbstract.search_panel,
    ]

    settings_panels = Page.settings_panels + [
        ArchiveablePageAbstract.archive_panel,
        BasicPageAbstract.submenu_panel,
        ThemeablePageAbstract.theme_panel,
    ]

    search_fields = ArchiveablePageAbstract.search_fields \
        + BasicPageAbstract.search_fields \
        + ContentPage.search_fields

    parent_page_types = ['core.BasicPage', 'research.ProjectListPage']
    subpage_types = []
    templates = 'research/project_page.html'

    def get_featured_pages(self):
        featured_page_ids = self.featured_pages.order_by('sort_order').values_list('featured_page', flat=True)
        pages = Page.objects.specific().prefetch_related(
            'authors__author',
            'topics',
        ).in_bulk(featured_page_ids)
        return [pages[x] for x in featured_page_ids]

    def get_template(self, request, *args, **kwargs):
        standard_template = super(ProjectPage, self).get_template(request, *args, **kwargs)
        if self.theme:
            return f'themes/{self.get_theme_dir()}/project_page.html'
        return standard_template

    def get_context(self, request):
        context = super().get_context(request)

        context['featured_pages'] = self.get_featured_pages()
        return context

    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'


class IgcTimelinePage(BasicPageAbstract, Page):
    """
    A special singleton page for /igc/timeline
    """

    max_count = 1
    parent_page_types = ['core.BasicPage']
    subpage_types = []
    templates = 'research/igc_timeline_page.html'

    body = StreamField(
        BasicPageAbstract.body_default_blocks + [
            ('igc_timeline', IgcTimelineBlock()),
        ],
        blank=True,
        use_json_field=True,
    )

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields

    class Meta:
        verbose_name = 'IGC Timeline Page'


class ProjectType(index.Indexed, models.Model):
    """
    A Django model that stores the project types. This isn't allowed to be
    edited in the admin interface. To insert/remove data - a migration needs to
    be created.
    """
    name = models.CharField(max_length=255)

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_taxonomy_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class ProjectPageFeaturedPage(Orderable):
    project_page = ParentalKey(
        'research.ProjectPage',
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


class ResearchLandingPage(BasicPageAbstract, Page):
    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = []
    templates = 'research/research_landing_page.html'
    featured_publications = StreamField(
        [
            ('publication', PublicationCard()),
        ],
        blank=True,
        use_json_field=True,
    )

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        FieldPanel('featured_publications'),
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields

    def topics_data(self):
        """Get the topics data for the research landing page"""
        topics = TopicPage.objects.live().filter(archive=0).order_by('title').annotate(count=Count('content_pages'), opinion_count=Count('content_pages__articlepage'), publication_count=Count('content_pages__publicationpage'), multimedia_count=Count('content_pages__multimediapage'), event_count=Count('content_pages__eventpage'))
        return {
            "name": "root",
            "children": [
                {
                    "name": topic.title,
                    "value": topic.count,
                    "url": topic.url,
                    "opinions": topic.opinion_count,
                    "publications": topic.publication_count,
                    "multimedia": topic.multimedia_count,
                    "events": topic.event_count,
                    "remainder": topic.count - topic.opinion_count - topic.publication_count - topic.multimedia_count - topic.event_count,
                }
                for topic in topics
            ]
        }

    class Meta:
        verbose_name = 'Research Landing Page'


class TopicListPage(Page):
    """Topic list page"""

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = ['research.TopicPage']
    templates = 'research/topic_list_page.html'

    class Meta:
        verbose_name = 'Topic List Page'


class TopicPage(
    ArchiveablePageAbstract,
    BasicPageAbstract,
    SearchablePageAbstract,
    Page
):
    """View topic page"""
    description = RichTextField(blank=True, null=False, features=['h2', 'h3', 'h4', 'hr', 'ol', 'ul', 'bold', 'italic', 'link'])

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_taxonomy_id = models.IntegerField(blank=True, null=True)

    layout = StreamField(
        [
            ('row', HomePageRow()),
        ],
        blank=True,
        use_json_field=True,
    )

    @property
    def featured_latest_pages(self):
        featured_page_ids = self.featured_pages.order_by('sort_order').values_list('featured_page', flat=True)
        pages = Page.objects.specific().prefetch_related(
            'authors__author',
            'topics',
        ).in_bulk(featured_page_ids)
        featured_pages = [pages[x] for x in featured_page_ids]
        if len(featured_pages) < 3:
            featured_pages = featured_pages + list(self.content_pages.specific().prefetch_related(
                'authors__author',
                'topics',
            ).live().exclude(articlepage=None).order_by('-publishing_date')[:(3 - len(featured_pages))])
        return featured_pages

    @property
    def topic_name(self):
        return self.title

    def topic_authors(self):
        return PersonPage.objects.live().filter(topics__id=self.id).order_by('last_name')

    def get_admin_display_title(self):
        return f"{self.title} (Archived)" if self.archive == 1 else self.title

    def __str__(self):
        return f"{self.title} (Archived)" if self.archive == 1 else self.title

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        MultiFieldPanel(
            [
                FieldPanel('layout'),
            ],
            heading='Layout', classname='collapsible collapsed home-page-layout',
        ),
    ]
    promote_panels = Page.promote_panels + [
        SearchablePageAbstract.search_panel,
    ]
    settings_panels = Page.settings_panels + [
        ArchiveablePageAbstract.archive_panel,
        BasicPageAbstract.submenu_panel,
    ]

    search_fields = Page.search_fields \
        + ArchiveablePageAbstract.search_fields \
        + SearchablePageAbstract.search_fields \
        + [
            index.SearchField('topic_name')
        ]

    parent_page_types = ['research.TopicListPage']
    subpage_types = []
    templates = 'research/topic_page.html'

    class Meta:
        indexes = [
            models.Index(fields=['archive'])
        ]
        verbose_name = 'Topic Page'
        verbose_name_plural = 'Topic Pages'


class TopicPageFeaturedPage(Orderable):
    topic_page = ParentalKey(
        'research.TopicPage',
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
            [
                'articles.ArticlePage',
                'articles.ArticleSeriesPage',
                'events.EventPage',
                'multimedia.MultimediaPage',
                'multimedia.MultimediaSeriesPage',
                'publications.PublicationPage',
                'publications.PublicationSeriesPage',
                'research.ProjectPage',
            ]
        )
    ]


class IssueListPage(Page):
    """Issue list page"""

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = ['research.IssuePage']
    templates = 'research/issue_list_page.html'

    class Meta:
        verbose_name = 'Issue List Page'


class IssuePage(ArchiveablePageAbstract,
                BasicPageAbstract,
                SearchablePageAbstract,
                Page):
    """View issue page"""
    description = RichTextField(blank=True, null=False, features=['h2', 'h3', 'h4', 'hr', 'ol', 'ul', 'bold', 'italic', 'link'])

    content_panels = Page.content_panels + [
        FieldPanel('description'),
    ]
    promote_panels = Page.promote_panels + [
        SearchablePageAbstract.search_panel,
    ]
    settings_panels = Page.settings_panels + [
        ArchiveablePageAbstract.archive_panel,
        BasicPageAbstract.submenu_panel,
    ]

    search_fields = Page.search_fields \
        + ArchiveablePageAbstract.search_fields \
        + SearchablePageAbstract.search_fields

    parent_page_types = ['research.IssueListPage']
    subpage_types = []
    templates = 'research/issue_page.html'

    class Meta:
        indexes = [
            models.Index(fields=['archive'])
        ]
        verbose_name = 'Issue Page'
        verbose_name_plural = 'Issue Pages'
