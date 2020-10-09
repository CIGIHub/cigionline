from core.models import (
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    FromTheArchivesPageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
)
from django.db import models
from modelcluster.fields import ParentalManyToManyField
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
from wagtail.core.models import Page
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel


class ArticleLandingPage(Page):
    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = []
    templates = 'articles/article_landing_page.html'

    class Meta:
        verbose_name = 'Article Landing Page'


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
    website_button_text = models.CharField(
        blank=True,
        max_length=64,
        help_text='Override the button text for the article website. If empty, the button will read "View Full Article".'
    )
    website_url = models.URLField(blank=True, max_length=512)
    works_cited = RichTextField(blank=True)

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

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
            ],
            heading='Media',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                InlinePanel('recommended'),
            ],
            heading='Recommended',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('topics'),
                FieldPanel('projects'),
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
    ]

    settings_panels = Page.settings_panels + [
        ThemeablePageAbstract.theme_panel,
    ]

    parent_page_types = ['articles.ArticleListPage']
    subpage_types = []
    templates = 'articles/article_page.html'

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
