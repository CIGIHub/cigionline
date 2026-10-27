from core.models import (
    ArchiveablePageAbstract,
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    SearchablePageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
    Auth0ProtectedPageAbstract,
)
from core.routers import RouterServeMixin
from django.db import models
from django.db.models import F
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from publications.models import T7PublicationPage
from streams.blocks import AdditionalFileBlock, FacetedListingBlock, SurveyFindingsCountryBlock, Think7ChairBlock
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
from streams.blocks import (
    IgcTimelineBlock,
    GESEventsBlock,
    GESHighlightsBlock,
    GESSlideBlock,
    GESSlideDeckBlock,
    GESDataBlock,
    GESRawDataBlock,
    PersonsListBlock,
    AccordionModuleBlock,
    BannerBlock,
    ComposableTabsBlock,
    CTAImageBlock,
    EventsCarouselBlock,
    ExpertsCarouselBlock,
    ExpertsGridBlock,
    GalleryTextBlock,
    ImageTextBlock,
    NewsCarouselBlock,
    NewsGridBlock,
    NewsletterSubscriptionBlock,
    NewsletterSignupCTABlock,
    ProgramGridBlock,
    ProgramsCarouselBlock,
    ProgramSpotlightBlock,
    ResourceBentoBlock,
    ResourceCarouselBlock,
    StatsBlock,
    SupportingMaterialsBlock,
    TextCardGridBlock,
    TrendingIssuesBlock,
    VideoCarouselBlock,
    VideoTextBlock,
)


class ProjectListPage(Page):
    max_count = 2
    parent_page_types = ['home.HomePage', 'home.Think7HomePage']
    subpage_types = ['research.ProjectPage']
    templates = 'research/project_list_page.html'

    body = StreamField(
        BasicPageAbstract.body_default_blocks,
        blank=True,
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    def get_template(self, request, *args, **kwargs):
        site = self.get_site()

        if site.site_name == 'Think 7 Canada':
            return 'think7/project_list_page.html'
        return super().get_template(request, *args, **kwargs)

    def get_task_forces(self):
        return self.get_children().type(ProjectPage).live().specific().annotate(publishing_date=F('contentpage__publishing_date')).order_by('publishing_date')

    class Meta:
        verbose_name = 'Activity List Page'


class ProjectPage(
    RouterServeMixin,
    Auth0ProtectedPageAbstract,
    ArchiveablePageAbstract,
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
):
    contact = RichTextField(
        blank=True,
        null=True,
        features=['h2', 'h3', 'h4', 'hr', 'ol', 'ul', 'bold', 'italic', 'link'],
    )
    body = StreamField(
        BasicPageAbstract.body_default_blocks + [
            BasicPageAbstract.body_composable_tabs_block,
            BasicPageAbstract.body_poster_block,
            BasicPageAbstract.body_recommended_block,
            BasicPageAbstract.body_text_border_block,
            ('additional_file', AdditionalFileBlock()),
            ('ges_events', GESEventsBlock()),
            ('ges_highlights', GESHighlightsBlock()),
            ('ges_slide', GESSlideBlock()),
            ('ges_slide_deck', GESSlideDeckBlock()),
            ('ges_data', GESDataBlock()),
            ('ges_raw_data', GESRawDataBlock()),
            ('chair', Think7ChairBlock()),
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
    video_banner = models.ForeignKey(
        'wagtailmedia.Media',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner Video',
    )
    # The alt hero's top/bottom gradient keeps white text legible over any
    # photo. Some hero images fight it (Tim, BugHerd #401: Space Governance),
    # so editors can switch it off per program. Program pages only.
    show_hero_overlay = models.BooleanField(
        default=True,
        verbose_name='Show photo vignette',
        help_text='The dark gradient over the hero background image. Turn off when it works against the photo.',
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
    additional_members = StreamField(
        [
            ('additional_members', PersonsListBlock()),
        ],
        blank=True,
    )
    project_types = ParentalManyToManyField('research.ProjectType', blank=True)
    related_files = StreamField(
        [
            ('file', DocumentChooserBlock()),
        ],
        blank=True,
        use_json_field=True,
    )
    survey_findings = StreamField(
        [
            ('country', SurveyFindingsCountryBlock()),
        ],
        blank=True,
        use_json_field=True,
        help_text='For OGBV theme only',
    )
    task_force_label = models.CharField(max_length=255, blank=True, null=True)
    featured_pages_format = models.CharField(
        max_length=20,
        choices=[
            ('standard', 'Standard'),
            ('medium_only', 'Medium Only'),
            ('large_only', 'Large Only'),
        ],
        default='standard',
        help_text='Select how featured content is displayed on the project page. Medium Only displays medium cards in rows of three. Large Only displays a large card in a single column.',
    )
    subscribe_page = models.ForeignKey(
        "wagtailcore.Page",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
        help_text="The newsletter subscription landing page for this project.",
    )

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        MultiFieldPanel(
            [
                FieldPanel('publishing_date'),
                FieldPanel('project_types'),
                FieldPanel('contact'),
            ],
            heading='General Information',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                InlinePanel(
                    'members',
                    label='Person',
                ),
                FieldPanel('additional_members'),
            ],
            heading='People',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('image_hero'),
                FieldPanel('show_hero_overlay'),
                FieldPanel('image_banner'),
                FieldPanel('video_banner'),
            ],
            heading='Images',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('topics'),
                FieldPanel('related_files'),
                FieldPanel('subscribe_page'),
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
                FieldPanel('featured_pages_format'),
            ],
            heading='Featured Content',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('survey_findings'),
                FieldPanel('task_force_label'),
            ],
            heading='Theme Content',
            classname='collapsible collapsed',
        )
    ]

    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        ShareablePageAbstract.social_panel,
        SearchablePageAbstract.search_panel,
    ]

    settings_panels = ContentPage.settings_panels + [
        ArchiveablePageAbstract.archive_panel,
        BasicPageAbstract.submenu_panel,
        ThemeablePageAbstract.theme_panel,
        ThemeablePageAbstract.surface_panel,
        Auth0ProtectedPageAbstract.auth0_protected_panel,
    ]

    search_fields = ArchiveablePageAbstract.search_fields \
        + BasicPageAbstract.search_fields \
        + ContentPage.search_fields

    parent_page_types = ['core.BasicPage', 'research.ProjectListPage']
    subpage_types = ['subscribe.TFGBVSubscribePage']
    templates = 'research/project_page.html'

    @property
    def has_tagged_pages(self):
        return ContentPage.objects.live().filter(projects=self).exists()

    @property
    def subscribe_button_text(self):
        if self.subscribe_page:
            return self.subscribe_page.specific.button_text or "Sign Up"
        return "Sign Up"

    @property
    def subscribe_help_text(self):
        if self.subscribe_page:
            return self.subscribe_page.specific.button_help_text or ""
        return ""

    def get_featured_pages(self):
        featured_page_ids = self.featured_pages.order_by('sort_order').values_list('featured_page', flat=True)
        pages = Page.objects.specific().prefetch_related(
            'authors__author',
            'topics',
        ).in_bulk(featured_page_ids)
        return [pages[x] for x in featured_page_ids]

    # Theme dirs that still keep a legacy microsite fork (retiring per
    # legacy-page-conversion-plan §7a). Any other theme (e.g. net-new program
    # shells like Responsible Technology) renders the DS template, mirroring
    # ArticlePage.ART_DIRECTED_THEME_DIRS.
    THEMED_FORK_DIRS = {'freedom_of_thought', 'ges', 'igc', 'nss', 'ogbv'}

    def theme_fork_template(self):
        # Shared with renders_legacy_fork, so a fork project's body blocks
        # render their pre-redesign templates too (BugHerd #522).
        if self.theme and self.get_theme_dir() in self.THEMED_FORK_DIRS:
            return f'themes/{self.get_theme_dir()}/project_page.html'
        return None

    def get_template(self, request, *args, **kwargs):
        site = self.get_site()

        if site.site_name == 'Think 7 Canada':
            return 'think7/project_page.html'

        standard_template = super(ProjectPage, self).get_template(request, *args, **kwargs)
        return self.theme_fork_template() or standard_template

    def get_additional_files(self):
        body = self.body
        additional_files = []
        for block in body:
            if block.block_type == 'additional_file':
                additional_files.append(block.value)
        return additional_files

    def get_taskforce_publications(self):
        return T7PublicationPage.objects.filter(taskforce=self).live().public().order_by('-publishing_date')

    def get_context(self, request):
        context = super().get_context(request)

        context['featured_pages'] = self.get_featured_pages()
        context['additional_files'] = self.get_additional_files()
        # Image alt-hero crumbs (BugHerd #77): same Home > Theme trail as the
        # content-hero presenter (standardized trail, IA 2026-08-26) — the
        # tree walk can't surface the theme, and both hero variants must agree.
        from core.heroes import _rel_url
        membership = self.theme_memberships.select_related('theme').first()
        crumbs = [{'title': 'Home', 'url': '/'}]
        if membership:
            crumbs.append({'title': membership.theme.title, 'url': _rel_url(membership.theme)})
        context['hero_crumbs'] = crumbs
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

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields

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
    program_theme = models.ForeignKey(
        'research.ThemePage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Program Theme',
    )

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_taxonomy_id = models.IntegerField(blank=True, null=True)

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
            ).live().exclude(
                articlepage=None
            ).exclude(
                articlepage__article_type__title='CIGI in the News'
            ).order_by('-publishing_date')[:(3 - len(featured_pages))])
        return featured_pages

    @property
    def topic_name(self):
        return self.title

    def get_admin_display_title(self):
        return f"{self.title} (Archived)" if self.archive == 1 else self.title

    def __str__(self):
        return f"{self.title} (Archived)" if self.archive == 1 else self.title

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        PageChooserPanel(
            'program_theme',
            ['research.ThemePage'],
        ),
        MultiFieldPanel(
            [
                InlinePanel(
                    'featured_pages',
                    max_num=3,
                    min_num=0,
                    label='Page',
                ),
            ],
            heading='Featured Content',
            classname='collapsible collapsed',
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


class ProjectPageMember(Orderable):
    project_page = ParentalKey('research.ProjectPage', related_name='members')
    member = models.ForeignKey(
        'people.PersonPage',
        on_delete=models.CASCADE,
        related_name='+',
    )

    panels = [
        PageChooserPanel('member', ['people.PersonPage']),
    ]


class ThemeListPage(Page):
    """Theme list page"""

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = ['research.ThemePage']
    templates = 'research/theme_list_page.html'

    class Meta:
        verbose_name = 'Theme List Page'


class ThemePage(
    # Serves the faceted listing's AJAX results partial (filter swaps, lazy tab
    # loads) — without it a filter click on a theme listing got the whole page
    # back. Needed now that the body hosts a listing directly (sync 2026-09-21).
    RouterServeMixin,
    ArchiveablePageAbstract,
    BasicPageAbstract,
    SearchablePageAbstract,
    Page,
):
    class Accents(models.TextChoices):
        AI_TECH = 'ai-tech', 'AI & Tech (blue)'
        DATA_ECONOMY = 'data-economy', 'Data & Economy (teal)'
        SECURITY = 'security', 'Security (olive)'
        GOVERNANCE = 'governance', 'Governance (mauve)'

    description = RichTextField(blank=True, null=False, features=['h2', 'h3', 'h4', 'hr', 'ol', 'ul', 'bold', 'italic', 'link'])
    accent = models.CharField(
        max_length=16,
        blank=True,
        choices=Accents.choices,
        help_text='Topic accent colour applied to this theme across the site.',
    )
    # Module-composed landing page (theme_page.html: hero + body). Same DS module
    # set as the homepage — themes are the same species of composed landing page —
    # minus the hero blocks (the theme hero is dev-owned; an authored hero would
    # double up). DS modules only, not the legacy prose blocks the
    # BasicPageAbstract default would inherit.
    body = StreamField(
        [
            ('banner', BannerBlock()),
            ('news_grid', NewsGridBlock()),
            ('news_carousel', NewsCarouselBlock()),
            ('experts_grid', ExpertsGridBlock()),
            ('experts_carousel', ExpertsCarouselBlock()),
            ('program_spotlight', ProgramSpotlightBlock()),
            ('program_grid', ProgramGridBlock()),
            ('programs_carousel', ProgramsCarouselBlock()),
            ('events_carousel', EventsCarouselBlock()),
            ('resource_carousel', ResourceCarouselBlock()),
            ('resource_bento', ResourceBentoBlock()),
            ('cta_image', CTAImageBlock()),
            ('image_text', ImageTextBlock()),
            ('text_card_grid', TextCardGridBlock()),
            ('stats', StatsBlock()),
            ('video_text', VideoTextBlock()),
            ('gallery_text', GalleryTextBlock()),
            ('trending_issues', TrendingIssuesBlock()),
            ('accordion_module', AccordionModuleBlock()),
            ('composable_tabs', ComposableTabsBlock()),
            ('supporting_materials', SupportingMaterialsBlock()),
            ('video_carousel', VideoCarouselBlock()),
            ('newsletter_subscription', NewsletterSubscriptionBlock()),
            ('newsletter_signup_cta', NewsletterSignupCTABlock()),
            # Top-level Faceted Listing (sync 2026-09-21): a topic pill lands on
            # the theme page's resource listing with the topic pre-selected
            # (core.router_links). The block already auto-scopes to the theme's
            # programs; before this it was placeable only inside Tabs.
            ('faceted_listing', FacetedListingBlock()),
        ],
        blank=True,
        use_json_field=True,
    )

    # semantic accent slug -> the colour-named accent classes in _surface.scss
    ACCENT_COLOURS = {
        Accents.AI_TECH: 'blue',
        Accents.DATA_ECONOMY: 'teal',
        Accents.SECURITY: 'olive',
        Accents.GOVERNANCE: 'mauve',
    }

    @property
    def theme_name(self):
        return self.title

    @property
    def accent_colour(self):
        return self.ACCENT_COLOURS.get(self.accent, 'red')

    @property
    def accent_surface_class(self):
        return f'ds-surface--accent-{self.accent_colour}' if self.accent else ''

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        FieldPanel('accent'),
        # Hero background image (BugHerd #61): with an image the page renders
        # the shared alt hero (image + breadcrumb + title + description);
        # without one it falls back to the accent-surface content hero.
        FieldPanel('image_hero', heading='Hero background image'),
        InlinePanel(
            'theme_programs',
            heading='Programs',
            label='Program',
            help_text='The programs listed under this theme, in display order.',
        ),
        # The theme page renders hero + body (theme_page.html) — authors compose
        # the programs/resource/expert/subscribe sections from DS modules. The
        # body panel was missing here, so content entry could only add programs.
        BasicPageAbstract.body_panel,
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
            index.SearchField('theme_name')
        ]

    parent_page_types = ['research.ThemeListPage']
    subpage_types = []
    templates = 'research/theme_page.html'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        # Theme pages are light. Body modules default to surface=inherit, which
        # needs a base surface on <main> to resolve the --surface-* tokens —
        # without one the token chain collapses and surface-drawn details (the
        # module-title top rule) vanish (BugHerd #63/#69).
        context['main_surface'] = 'light'
        if self.accent:
            context['main_accent_scheme'] = self.accent_colour
        # Standardized trail (IA 2026-08-26, supersedes #341's Home > Topics):
        # a theme sits right under Home in the trail, and the current page
        # drops per #152 — so a theme page shows Home alone.
        context['hero_crumbs'] = [{'title': 'Home', 'url': '/'}]
        # Theme pages lead with the dark image hero, so the nav is dark too
        # (BugHerd #73) — same treatment as the homepage.
        context['header_surface'] = 'dark'
        return context

    class Meta:
        indexes = [
            models.Index(fields=['archive'])
        ]
        verbose_name = 'Theme Page'
        verbose_name_plural = 'Theme Pages'


class ThemeProgram(Orderable):
    """
    The authoritative theme -> program edge. A program appears under a theme
    only if a row exists here; ordering is editorial (drag in the InlinePanel).
    """
    theme = ParentalKey('research.ThemePage', related_name='theme_programs')
    program = models.ForeignKey(
        'research.ProjectPage',
        on_delete=models.CASCADE,
        related_name='theme_memberships',
    )
    label = models.CharField(
        max_length=255,
        blank=True,
        help_text='Optional display label; defaults to the program page title.',
    )

    panels = [
        PageChooserPanel('program', ['research.ProjectPage']),
        FieldPanel('label'),
    ]

    @property
    def display_title(self):
        return self.label or self.program.title


class CountryListPage(Page):
    """Country list page"""

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = ['research.CountryPage']
    templates = 'research/country_list_page.html'

    class Meta:
        verbose_name = 'Country List Page'


class CountryPage(
    ArchiveablePageAbstract,
    BasicPageAbstract,
    SearchablePageAbstract,
    Page
):
    """View country page"""
    description = RichTextField(blank=True, null=False, features=['h2', 'h3', 'h4', 'hr', 'ol', 'ul', 'bold', 'italic', 'link'])
    alpha_2_code = models.CharField(max_length=2, blank=True, null=True)
    alpha_3_code = models.CharField(max_length=3, blank=True, null=True)
    numeric_code = models.CharField(max_length=3, blank=True, null=True)
    display_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Override political name with common name for tag display.'
    )

    @property
    def country_name(self):
        return self.title

    @property
    def featured_latest_pages(self):
        featured_page_ids = self.featured_pages.order_by('sort_order').values_list('featured_page', flat=True)
        pages = Page.objects.specific().prefetch_related(
            'authors__author',
            'countries',
        ).in_bulk(featured_page_ids)
        featured_pages = [pages[x] for x in featured_page_ids]
        if len(featured_pages) < 3:
            featured_pages = featured_pages + list(self.content_pages.specific().prefetch_related(
                'authors__author',
                'countries',
            ).live().exclude(
                articlepage=None
            ).exclude(
                articlepage__article_type__title='CIGI in the News'
            ).order_by('-publishing_date')[:(3 - len(featured_pages))])
        return featured_pages

    def __str__(self):
        return f"{self.title} (Archived)" if self.archive == 1 else self.title

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        FieldPanel('display_name'),
        MultiFieldPanel(
            [
                FieldPanel('alpha_2_code'),
                FieldPanel('alpha_3_code'),
                FieldPanel('numeric_code'),

            ],
            heading='General Information',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                InlinePanel(
                    'featured_pages',
                    max_num=3,
                    min_num=0,
                    label='Page',
                ),
            ],
            heading='Featured Content',
            classname='collapsible collapsed',
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
            index.SearchField('country_name')
        ]

    parent_page_types = ['research.CountryListPage']
    subpage_types = []
    templates = 'research/country_page.html'

    class Meta:
        verbose_name = 'Country Page'
        verbose_name_plural = 'Country Pages'


class CountryPageFeaturedPage(Orderable):
    country_page = ParentalKey(
        'research.CountryPage',
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
