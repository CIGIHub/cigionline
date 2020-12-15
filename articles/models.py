from core.models import (
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    FromTheArchivesPageAbstract,
    SearchablePageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
)
from django.db import models
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.core.blocks import (
    CharBlock,
    PageChooserBlock,
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailmedia.edit_handlers import MediaChooserPanel


class ArticleLandingPage(Page):
    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = []
    templates = 'articles/article_landing_page.html'

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                InlinePanel(
                    'featured_articles',
                    max_num=15,
                    min_num=13,
                    label='Article',
                )
            ],
            heading='Featured Opinions',
            classname='collapsible collapsed',
        )
    ]

    class Meta:
        verbose_name = 'Article Landing Page'


class ArticleLandingPageFeaturedArticle(Orderable):
    article_landing_page = ParentalKey(
        'articles.ArticleLandingPage',
        related_name='featured_articles',
    )
    article_page = models.ForeignKey(
        'articles.ArticlePage',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Article',
    )

    panels = [
        PageChooserPanel(
            'article_page',
            ['articles.ArticlePage'],
        ),
    ]


class ArticleListPage(Page):
    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = ['articles.ArticlePage']
    templates = 'articles/article_list_page.html'

    class Meta:
        verbose_name = 'Article List Page'


class ArticlePage(
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    FromTheArchivesPageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
):
    class ArticleTypes(models.TextChoices):
        CIGI_IN_THE_NEWS = ('cigi_in_the_news', 'CIGI in the News')
        INTERVIEW = ('interview', 'Interview')
        NEWS_RELEASE = ('news_release', 'News Release')
        OP_ED = ('op_ed', 'Op-Ed')
        OPINION = ('opinion', 'Opinion')

    class Languages(models.TextChoices):
        DA = ('da', 'Danish')
        DE = ('de', 'German')
        EL = ('el', 'Greek')
        EN = ('en', 'English')
        ES = ('es', 'Spanish')
        FR = ('fr', 'French')
        ID = ('id', 'Indonesian')
        IT = ('it', 'Italian')
        NL = ('nl', 'Dutch')
        PL = ('pl', 'Polish')
        PT = ('pt', 'Portugese')
        RO = ('ro', 'Romanian')
        SK = ('sk', 'Slovak')
        SV = ('sv', 'Swedish')
        TR = ('tr', 'Turkish')
        ZH = ('zh', 'Chinese')

    class HeroTitlePlacements(models.TextChoices):
        BOTTOM = ('bottom', 'Bottom')
        TOP = ('top', 'Top')

    article_series = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Opinion series',
    )
    article_type = models.CharField(
        blank=False,
        max_length=32,
        choices=ArticleTypes.choices,
    )
    authors = StreamField(
        [
            ('author', PageChooserBlock(required=True, page_type='people.PersonPage')),
            ('external_author', CharBlock(required=True)),
        ],
        blank=True,
    )
    cigi_people_mentioned = StreamField(
        [
            ('cigi_person', PageChooserBlock(required=True, page_type='people.PersonPage')),
        ],
        blank=True,
    )
    embed_youtube = models.URLField(
        blank=True,
        verbose_name='YouTube Embed',
        help_text='Enter the YouTube URL (https://www.youtube.com/watch?v=4-Xkn1U1DkA) or short URL (https://youtu.be/o5acQ2GxKbQ) to add an embedded video.',
    )
    embed_youtube_label = models.CharField(
        max_length=255,
        blank=True,
        help_text='Add a label to appear below the embedded video.',
    )
    footnotes = RichTextField(blank=True)
    hero_title_placement = models.CharField(
        blank=True,
        max_length=16,
        choices=HeroTitlePlacements.choices,
        verbose_name='Hero Title Placement',
        help_text='Placement of the title within the hero section. Currently only works on the Longform 2 theme.',
    )
    image_banner = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner Image',
    )
    image_banner_small = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner Image Small'
    )
    interviewers = StreamField(
        [
            ('interviewer', PageChooserBlock(required=True, page_type='people.PersonPage')),
        ],
        blank=True,
    )
    language = models.CharField(
        blank=True,
        max_length=2,
        choices=Languages.choices,
        verbose_name='Language',
        help_text='If this content is in a language other than English, please select the language from the list.',
    )
    multimedia_series = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    projects = ParentalManyToManyField('research.ProjectPage', blank=True)
    related_files = StreamField(
        [
            ('file', DocumentChooserBlock()),
        ],
        blank=True,
    )
    video_banner = models.ForeignKey(
        'wagtailmedia.Media',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner Video',
    )
    website_button_text = models.CharField(
        blank=True,
        max_length=64,
        help_text='Override the button text for the article website. If empty, the button will read "View Full Article".'
    )
    website_url = models.URLField(blank=True, max_length=512)
    works_cited = RichTextField(blank=True)

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    def get_template(self, request, *args, **kwargs):
        standard_template = super(ArticlePage, self).get_template(request, *args, **kwargs)
        if self.theme and self.theme.name == 'Longform':
            return 'themes/longform/article_page.html'
        return standard_template

    content_panels = [
        BasicPageAbstract.title_panel,
        MultiFieldPanel(
            [
                StreamFieldPanel('body'),
                FieldPanel('footnotes'),
                FieldPanel('works_cited'),
            ],
            heading='Body',
            classname='collapsible'
        ),
        MultiFieldPanel(
            [
                FieldPanel('article_type'),
                FieldPanel('publishing_date'),
                FieldPanel('website_url'),
                FieldPanel('website_button_text'),
                FieldPanel('language'),
            ],
            heading='General Information',
            classname='collapsible',
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('authors'),
            ],
            heading='Authors',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel('image_hero'),
                ImageChooserPanel('image_banner'),
                ImageChooserPanel('image_banner_small'),
            ],
            heading='Images',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('embed_youtube'),
                FieldPanel('embed_youtube_label'),
                MediaChooserPanel('video_banner'),
            ],
            heading='Media',
            classname='collapsible collapsed',
        ),
        ContentPage.recommended_panel,
        MultiFieldPanel(
            [
                FieldPanel('topics'),
                FieldPanel('projects'),
                PageChooserPanel(
                    'article_series',
                    ['articles.ArticleSeriesPage'],
                ),
                PageChooserPanel(
                    'multimedia_series',
                    ['multimedia.MultimediaSeriesPage'],
                ),
                StreamFieldPanel('cigi_people_mentioned'),
                StreamFieldPanel('interviewers'),
                StreamFieldPanel('related_files'),
            ],
            heading='Related',
            classname='collapsible collapsed',
        ),
        FromTheArchivesPageAbstract.from_the_archives_panel,
    ]

    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        ShareablePageAbstract.social_panel,
        SearchablePageAbstract.search_panel,
    ]

    settings_panels = Page.settings_panels + [
        ThemeablePageAbstract.theme_panel,
    ]

    parent_page_types = ['articles.ArticleListPage']
    subpage_types = []
    templates = 'articles/article_page.html'

    class Meta:
        verbose_name = 'Opinion'
        verbose_name_plural = 'Opinions'


class ArticleSeriesPage(
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    FromTheArchivesPageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
):
    credits = RichTextField(blank=True)
    credits_artwork = models.CharField(
        max_length=255,
        blank=True,
    )
    image_banner = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner Image',
    )
    image_banner_small = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner Image Small'
    )
    image_poster = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Poster image',
        help_text='A poster image which will be used in the highlights section of the homepage.',
    )
    series_items = StreamField(
        [
            ('series_item', PageChooserBlock(
                required=True,
                page_type=['articles.ArticlePage', 'multimedia.MultimediaPage'],
            )),
            ('category_title', CharBlock(required=True)),
        ],
        blank=True,
    )
    short_description = RichTextField(
        blank=True,
        null=False,
        features=['bold', 'italic'],
    )
    video_banner = models.ForeignKey(
        'wagtailmedia.Media',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner Video',
    )

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    content_panels = [
        BasicPageAbstract.title_panel,
        MultiFieldPanel(
            [
                FieldPanel('short_description'),
                StreamFieldPanel('body'),
            ],
            heading='Body',
            classname='collapsible',
        ),
        MultiFieldPanel(
            [
                FieldPanel('publishing_date'),
            ],
            heading='General Information',
            classname='collapsible',
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('series_items'),
            ],
            heading='Series Items',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('credits'),
                FieldPanel('credits_artwork'),
            ],
            heading='Credits',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel('image_hero'),
                ImageChooserPanel('image_banner'),
                ImageChooserPanel('image_banner_small'),
                ImageChooserPanel('image_poster'),
            ],
            heading='Image',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                MediaChooserPanel('video_banner'),
            ],
            heading='Media',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('topics'),
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

    parent_page_types = ['core.HomePage']
    subpage_types = []
    templates = 'articles/article_series_page.html'

    class Meta:
        verbose_name = 'Opinion Series'
        verbose_name_plural = 'Opinion Series'
