from collections import OrderedDict
from bs4 import BeautifulSoup
from core.models import (
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    FromTheArchivesPageAbstract,
    HeroPodcastTogglesAbstract,
    SearchablePageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
)
from django.db.models.fields import CharField
from django.db import models
from modelcluster.fields import ParentalKey
from streams.blocks import (
    PodcastFollowButtonBlock,
    PodcastSubscribeButtonBlock,
    FeaturedEpisodeBlock,
    PodcastHostBlock,
    PodcastChapterBlock,
    PodcastGuestBlock,
    PodcastTranscriptBlock,
)
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.blocks import (
    CharBlock,
    IntegerBlock,
    StructBlock,
    TextBlock,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index
import re


class MultimediaListPage(BasicPageAbstract, SearchablePageAbstract, Page):
    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = ['multimedia.MultimediaPage']
    template = 'multimedia/multimedia_list_page.html'
    ajax_template = 'includes/multimedia_list_page_multimedia_list.html'

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
        MultiFieldPanel(
            [
                InlinePanel(
                    'featured_multimedia',
                    max_num=6,
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
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields + SearchablePageAbstract.search_fields

    def get_featured_multimedia(self):
        featured_multimedia_ids = self.featured_multimedia.order_by('sort_order').values_list('multimedia_page', flat=True)
        pages = Page.objects.specific().prefetch_related(
            'authors__author',
            'topics',
        ).in_bulk(featured_multimedia_ids)
        return [pages[x] for x in featured_multimedia_ids]

    def get_promotion_blocks(self):
        return self.promotion_blocks.prefetch_related(
            'promotion_block',
        ).all()[:1]

    def get_context(self, request):
        context = super().get_context(request)
        context['featured_multimedia'] = self.get_featured_multimedia()
        context['promotion_blocks'] = self.get_promotion_blocks()
        return context

    class Meta:
        verbose_name = 'Multimedia List Page'


class MultimediaListPageFeaturedMultimedia(Orderable):
    multimedia_list_page = ParentalKey(
        'multimedia.MultimediaListPage',
        related_name='featured_multimedia',
    )
    multimedia_page = models.ForeignKey(
        'wagtailcore.Page',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Multimedia',
    )

    panels = [
        PageChooserPanel(
            'multimedia_page',
            ['multimedia.MultimediaPage'],
        )
    ]


class MultimediaPage(
    BasicPageAbstract,
    HeroPodcastTogglesAbstract,
    ContentPage,
    FeatureablePageAbstract,
    FromTheArchivesPageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
):
    class MultimediaTypes(models.TextChoices):
        AUDIO = ('audio', 'Audio')
        VIDEO = ('video', 'Video')

    article_series = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Opinion series',
    )
    companion_essay = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Companion essay',
    )
    image_banner = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner Image',
    )
    image_poster = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Poster Image',
        help_text='A poster image used in feature sections',
    )
    image_square = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Square image',
    )
    length = models.CharField(
        blank=True,
        max_length=8,
        verbose_name='Length',
        help_text='| CIGI 3.0 field | The length of the multimedia source in minutes and seconds (e.g. 1:23).',
    )
    multimedia_series = models.ForeignKey(
        'multimedia.MultimediaSeriesPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    multimedia_type = models.CharField(
        blank=False,
        max_length=8,
        choices=MultimediaTypes.choices,
        default=MultimediaTypes.VIDEO,
    )
    multimedia_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name='Multimedia URL',
        help_text='The URL of the multimedia source from YouTube or Simplecast.',
    )
    podcast_audio_duration = models.CharField(blank=True, max_length=8)
    podcast_audio_file_size = models.IntegerField(blank=True, null=True)
    podcast_audio_url = models.URLField(blank=True)
    podcast_recording_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Recording Date',
    )
    podcast_episode = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Episode Number',
    )
    podcast_guests = StreamField(
        [
            ('guest', CharBlock(required=True)),
            ('guest_page', PodcastGuestBlock()),
        ],
        blank=True,
        use_json_field=True,
        help_text='A list of guests for the podcast. If the guest has a page on the site, you can link to it here.',
    )
    podcast_season = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Season Number',
    )
    podcast_subtitle = models.CharField(blank=True, max_length=255)
    podcast_video_duration = models.CharField(blank=True, max_length=8)
    podcast_video_file_size = models.IntegerField(blank=True, null=True)
    podcast_video_url = models.URLField(blank=True)
    short_description = RichTextField(
        blank=True,
        null=False,
        features=['bold', 'italic', 'link'],
    )
    podcast_chapters = StreamField(
        [
            ('podcast_chapter', PodcastChapterBlock())
        ],
        blank=True,
        verbose_name='Podcast Chapters',
        help_text='A list of chapters for the podcast',
        use_json_field=True,
    )
    transcript = StreamField(
        [
            BasicPageAbstract.body_accordion_block,
            BasicPageAbstract.body_read_more_block,
            ('transcript_block', PodcastTranscriptBlock()),
        ],
        blank=True,
        use_json_field=True,
    )
    video_chapters = StreamField(
        [
            ('video_chapter', StructBlock([
                ('chapter_title', CharBlock(required=True)),
                ('location_time', IntegerBlock(required=True)),
                ('chapter_description', TextBlock(required=False)),
            ])),
        ],
        blank=True,
        use_json_field=True,
    )
    vimeo_url = models.URLField(
        blank=True,
        verbose_name='Vimeo URL',
        help_text='| CIGI 3.0 field | The URL of the multimedia source from Vimeo.',
    )
    youtube_id = models.CharField(
        blank=True,
        max_length=32,
        verbose_name='YouTube ID',
        help_text='Enter just the YouTube ID for this video. This is the series of letters and numbers found either at www.youtube.com/embed/[here], or www.youtube.com/watch?v=[here]. This is used for the video chaptering below.',
    )

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    @property
    def article_series_description(self):
        if self.article_series:
            if self.article_series.specific.series_videos_description:
                return self.article_series.specific.series_videos_description
            return self.article_series.specific.series_items_description
        return None

    @property
    def ds_surface(self):
        # Pink is the POLICY PROMPT brand, whole-single (hero to footer) — not
        # a generic podcast treatment. Non-PP audio and video singles render
        # on the default light surface, per the recorded multimedia single
        # frame 1437:71269 (BugHerd #312; Evan, 2026-08-27; revisit with #408).
        from core.heroes import POLICY_PROMPT_SERIES_SLUG
        return 'pink' if (
            self.multimedia_type == 'audio'
            and self.multimedia_series is not None
            and self.multimedia_series.slug == POLICY_PROMPT_SERIES_SLUG
        ) else 'light'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        # The <main> wrapper carries the page surface so every section —
        # including the legacy disclaimer/archives ones — sits on it. The
        # site header follows: podcast pages are pink from the nav down.
        context['main_surface'] = self.ds_surface
        if self.ds_surface == 'pink':
            context['header_surface'] = 'pink'
        # Series brand accent (Podcast Template): heading colours/rules pick
        # it up via --accent on <main>. The hero re-scopes its own accent, so
        # player chrome stays red.
        if self.multimedia_type == 'audio' and self.multimedia_series:
            colour = getattr(self.multimedia_series.specific, 'brand_colour', '')
            if colour:
                context['main_accent'] = colour
        return context

    legacy_fork_template = 'multimedia_page.html'

    def get_template(self, request, *args, **kwargs):
        # A themed episode (Policy Prompt, Big Tech, series skins) keeps its
        # pre-redesign design (CIGI, sync 2026-09-21). Unthemed audio/video
        # renders the DS podcast single; series identity there comes from
        # multimedia_series data, with the Policy Prompt logo as hero fallback.
        standard_template = super(MultimediaPage, self).get_template(request, *args, **kwargs)
        return self.themed_template(self.legacy_fork_template, standard_template)

    def podcast_episode_minutes(self):
        return int(self.podcast_audio_duration.split(':')[0])

    def next_episode(self):
        if self.podcast_episode is None:
            return None
        next_episode_number = self.podcast_episode + 1
        season_number = self.podcast_season
        return MultimediaPage.objects.filter(multimedia_series=self.multimedia_series, podcast_episode=next_episode_number, podcast_season=season_number).first()

    def get_transcript(self):
        soup = BeautifulSoup(self.transcript[0].value['text'].source, 'html.parser')
        parsed_transcript = []
        paragraphs = soup.find_all('p')
        pattern = r"(?P<name>.*?)\s*\((?P<role>host|guest)\):"
        current_speaker = None
        current_role = None
        current_text = []

        for para in paragraphs:
            text = para.get_text(strip=True)
            match = re.match(pattern, text, flags=re.IGNORECASE)
            if match:
                if current_speaker:
                    parsed_transcript.append({
                        'name': current_speaker,
                        'role': current_role,
                        'text': ''.join(current_text)
                    })
                current_speaker = match.group('name').strip()
                current_role = match.group('role').strip()
                current_text = []
            else:
                current_text.append(str(para))

        if current_speaker:
            parsed_transcript.append({
                'name': current_speaker,
                'role': current_role,
                'text': ''.join(current_text)
            })

        return parsed_transcript

    content_panels = [
        BasicPageAbstract.title_panel,
        MultiFieldPanel(
            [
                FieldPanel('short_description'),
                FieldPanel('body'),
            ],
            heading='Body',
            classname='collapsible collapsed'
        ),
        MultiFieldPanel(
            [
                FieldPanel('multimedia_type'),
                FieldPanel('publishing_date'),
                FieldPanel('multimedia_url'),
                FieldPanel('vimeo_url'),
                FieldPanel('length'),
            ],
            heading='General Information',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                InlinePanel('authors'),
            ],
            heading='Speakers',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('youtube_id'),
                FieldPanel('video_chapters'),
            ],
            heading='Video Chapters',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('transcript'),
            ],
            heading='Transcript',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('podcast_subtitle'),
                FieldPanel('podcast_season'),
                FieldPanel('podcast_episode'),
                FieldPanel('podcast_guests'),
                FieldPanel('podcast_chapters'),
                MultiFieldPanel(
                    [
                        FieldPanel('podcast_audio_url'),
                        FieldPanel('podcast_audio_duration'),
                        FieldPanel('podcast_audio_file_size'),
                        FieldPanel('podcast_recording_date'),
                    ],
                    heading='Audio',
                    classname='collapsible collapsed',
                ),
                MultiFieldPanel(
                    [
                        FieldPanel('podcast_video_url'),
                        FieldPanel('podcast_video_duration'),
                        FieldPanel('podcast_video_file_size'),
                    ],
                    heading='Video',
                    classname='collapsible collapsed',
                ),
            ],
            heading='Podcast Details',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('image_hero'),
                FieldPanel('image_banner'),
                FieldPanel('image_square'),
                FieldPanel('image_poster'),
            ],
            heading='Images',
            classname='collapsible collapsed',
        ),
        ContentPage.recommended_panel,
        MultiFieldPanel(
            [
                PageChooserPanel(
                    'multimedia_series',
                    ['multimedia.MultimediaSeriesPage'],
                ),
                PageChooserPanel(
                    'article_series',
                    ['articles.ArticleSeriesPage'],
                ),
                PageChooserPanel(
                    'companion_essay',
                    ['articles.ArticlePage'],
                ),
                FieldPanel('topics'),
                FieldPanel('projects'),
            ],
            heading='Related',
            classname='collapsible collapsed',
        ),
        FromTheArchivesPageAbstract.from_the_archives_panel,
        HeroPodcastTogglesAbstract.hero_options_panel,
    ]
    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        ShareablePageAbstract.social_panel,
        SearchablePageAbstract.search_panel,
    ]
    settings_panels = ContentPage.settings_panels + [
        ThemeablePageAbstract.theme_panel,
    ]

    search_fields = BasicPageAbstract.search_fields \
        + ContentPage.search_fields \
        + [
            index.FilterField('multimedia_series'),
            index.FilterField('multimedia_type'),
            index.FilterField('publishing_date'),
        ]

    parent_page_types = ['multimedia.MultimediaListPage', 'multimedia.MultimediaSeriesPage']
    subpage_types = []
    templates = 'multimedia/multimedia_page.html'

    class Meta:
        verbose_name = 'Multimedia'
        verbose_name_plural = 'Multimedia'


class MultimediaSeriesListPage(Page):
    """
    A singleton page that isn't published, but is the parent to all the
    multimedia series pages at the path /multimedia-series.
    """
    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = ['multimedia.MultimediaSeriesPage']
    templates = 'multimedia/multimedia_series_list_page.html'

    class Meta:
        verbose_name = 'Multimedia Series List Page'


class MultimediaSeriesPage(
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
):
    credits = RichTextField(
        blank=True,
        null=False,
        features=['bold', 'italic', 'link'],
    )
    featured_episodes = StreamField(
        [
            ('featured_episode', FeaturedEpisodeBlock()),
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
    image_logo = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Series Logo',
    )
    image_poster = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Poster Image',
        help_text='A poster image which will be used in the highlights section of the homepage.',
    )
    podcast_season_tagline = CharField(blank=True, null=True, max_length=256)
    podcast_subscribe_buttons = StreamField([
        ('podcast_subscribe_button', PodcastSubscribeButtonBlock())
    ],
        blank=True,
        verbose_name='Podcast Subscribe Buttons',
        help_text='A list of subscribe links to various podcast providers',
        use_json_field=True,
    )
    podcast_follow_buttons = StreamField([
        ('podcast_follow_button', PodcastFollowButtonBlock())
    ],
        blank=True,
        verbose_name='Podcast Follow Buttons',
        help_text="The series' social accounts, shown as the hero 'Follow' group.",
        use_json_field=True,
    )
    podcast_hosts = StreamField([
        ('podcast_host', PodcastHostBlock())
    ],
        blank=True,
        verbose_name='Podcast Hosts',
        help_text='Hosts of the podcast',
        use_json_field=True
    )
    podcast_hosts_description = RichTextField(
        blank=True,
        features=['bold', 'italic', 'link'],
        verbose_name='Hosts description',
        help_text='Short intro under the "Experts / Hosts" heading on every '
                  'episode\'s sidebar.',
    )
    brand_colour = models.CharField(
        blank=True,
        max_length=7,
        verbose_name='Brand colour (hex)',
        help_text='Series brand accent, e.g. #325ab2 (Policy Prompt blue). '
                  'Drives episode-page heading colours and rules; leave blank '
                  'for the default red accent.',
    )
    podcast_live = models.BooleanField(default=False)

    @property
    def series_seasons_big_tech(self):
        episode_filter = {
            'multimedia_series': self,
            'theme__name__in': [
                'Big Tech S3',
                'Big Tech',
            ]
        }
        series_episodes = MultimediaPage.objects.filter(**episode_filter).order_by('-publishing_date')
        series_seasons = {}
        for episode in series_episodes:
            episode_season = episode.specific.podcast_season
            if episode_season not in series_seasons:
                series_seasons.update({episode_season: {'published': [], 'unpublished': []}})
            if episode.live:
                series_seasons[episode_season]['published'].append(episode)
            else:
                series_seasons[episode_season]['unpublished'].append(episode)

        return series_seasons

    @property
    def series_seasons(self):
        episode_filter = {'multimedia_series': self}
        series_episodes = MultimediaPage.objects.filter(**episode_filter).order_by('-publishing_date')
        seasons = {}
        for episode in series_episodes:
            season = episode.specific.podcast_season or 0
            if season not in seasons:
                seasons[season] = {'published': [], 'unpublished': []}
            (seasons[season]['published'] if episode.live else seasons[season]['unpublished']).append(episode)

        return OrderedDict(sorted(seasons.items(), key=lambda x: x[0]))

    @property
    def latest_episode(self):
        return MultimediaPage.objects.filter(multimedia_series=self).live().latest('publishing_date')

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    # Body adds the placeable faceted-listing module so a series landing can host
    # the "All Episodes" listing (episode_row cards + a Season facet,
    # auto-scoped to this series) plus the composable Tabs block.
    body = StreamField(
        BasicPageAbstract.body_default_blocks + [
            BasicPageAbstract.body_composable_tabs_block,
            BasicPageAbstract.body_faceted_listing_block,
        ],
        blank=True,
        use_json_field=True,
    )

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        MultiFieldPanel(
            [
                FieldPanel('publishing_date'),
                FieldPanel('credits'),
            ],
            heading='General Information',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('image_hero'),
                FieldPanel('image_banner'),
                FieldPanel('image_poster'),
            ],
            heading='Images',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('image_logo'),
                FieldPanel('podcast_hosts'),
                FieldPanel('podcast_hosts_description'),
                FieldPanel('brand_colour'),
                FieldPanel('podcast_season_tagline'),
                FieldPanel('podcast_subscribe_buttons'),
                FieldPanel('podcast_follow_buttons'),
                FieldPanel('podcast_live'),
            ],
            heading='Podcast Details',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('topics'),
                FieldPanel('projects'),
            ],
            heading='Related',
            classname='collapsible collapsed',
        ),
    ]
    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        ShareablePageAbstract.social_panel,
        SearchablePageAbstract.search_panel,
    ]
    settings_panels = Page.settings_panels + [
        ThemeablePageAbstract.theme_panel,
    ]
    search_fields = ContentPage.search_fields + BasicPageAbstract.search_fields

    parent_page_types = ['home.HomePage', 'multimedia.MultimediaSeriesListPage']
    subpage_types = ['multimedia.MultimediaPage']
    templates = 'multimedia/multimedia_series_page.html'

    def get_template(self, request, *args, **kwargs):
        # A themed series home keeps its pre-redesign design (CIGI, sync
        # 2026-09-21: /pp/ and Big Tech revert to their legacy pages).
        standard_template = super(MultimediaSeriesPage, self).get_template(request, *args, **kwargs)
        return self.themed_template('multimedia_series_page.html', standard_template)

    def _episodes_listing_value(self):
        """Faceted-listing value for the All Episodes router;
        auto series scope resolves to this page."""
        return {
            'prefix': 'ep',
            'card_type': 'episode_row',
            'heading': 'All Episodes',
            # Season list + collapsed Year facet (series-home design 1312:29981).
            'facets': ['season', 'year'],
            'per_page': 12,
        }

    def latest_episode(self):
        from multimedia.models import MultimediaPage
        return (MultimediaPage.objects.live().public()
                .filter(multimedia_series=self, publishing_date__isnull=False)
                .order_by('-publishing_date').first())

    def is_podcast(self):
        """Podcast (audio) series get the pink Podcast Template treatment; video
        series (Speaker Series, Inside Issues, …) stay on the default light
        surface. MultimediaSeriesPage has no media-type field, so derive it from
        the episodes — same signal the episode single uses (multimedia_type)."""
        from multimedia.models import MultimediaPage
        return MultimediaPage.objects.live().filter(
            multimedia_series=self, multimedia_type='audio').exists()

    def get_context(self, request, *args, **kwargs):
        from core.faceted_listing import build_listing_context
        context = super().get_context(request, *args, **kwargs)
        context.update(build_listing_context(request, self._episodes_listing_value(), page=self))
        context['latest_episode'] = self.latest_episode()
        # Pink is the POLICY PROMPT brand (BugHerd #312): only the PP series
        # home gets the pink chrome; other series — podcast or video — render
        # on the default light surface (gated in the template too).
        from core.heroes import POLICY_PROMPT_SERIES_SLUG
        context['is_podcast'] = self.is_podcast()
        context['is_pp_series'] = self.slug == POLICY_PROMPT_SERIES_SLUG
        if context['is_pp_series']:
            context['header_surface'] = 'pink'
        # Series brand accent on <main> (--brand-accent): the All Episodes
        # router chrome takes it where set (1366:133899 — PP blue), same
        # mechanism as the episode single.
        if self.brand_colour:
            context['main_accent'] = self.brand_colour

        # "The Hosts" (series home): the shared experts-carousel module,
        # data-driven — series hosts as expert cards on the pink surface, with
        # the authorable podcast_hosts_description as the intro.
        hosts = [
            b.value['host'].specific for b in (self.podcast_hosts or [])
            if b.value.get('host') and b.value['host'].live
        ]
        context['host_pages'] = [h for h in hosts if not getattr(h, 'archive', False)]
        if context['host_pages']:
            from people.models import PersonListPage
            experts_page = PersonListPage.objects.live().filter(slug='experts').first()
            context['hosts_cta_url'] = experts_page.get_url(request) if experts_page else None
            context['hosts_cfg'] = {
                'surface': 'pink' if context['is_pp_series'] else 'light',
                'accent': 'red', 'heading': 'The Hosts',
                'intro': self.podcast_hosts_description,
                'cta_label': 'Browse All Experts',
                'show_pagination': False,
                'card_slots': {'show_title': True, 'show_read_bio': True},
            }
        return context

    def serve(self, request, *args, **kwargs):
        # AJAX filter/pagination requests get the results partial (same contract
        # as RouterServeMixin's page-level shape).
        from core.routers import is_ajax, router_partial_response
        if is_ajax(request) and request.GET.get('router') == 'ep':
            from core.faceted_listing import build_listing_context
            context = build_listing_context(request, self._episodes_listing_value(), page=self)
            return router_partial_response(request, context)
        return super().serve(request, *args, **kwargs)

    class Meta:
        verbose_name = 'Multimedia Series'
        verbose_name_plural = 'Multimedia Series'


class MultimediaListPagePromotionBlocks(Orderable):
    multimedia_list_page = ParentalKey(
        'multimedia.MultimediaListPage',
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
