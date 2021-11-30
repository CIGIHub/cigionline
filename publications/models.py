from core.models import (
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    FromTheArchivesPageAbstract,
    SearchablePageAbstract,
    ShareablePageAbstract,
)
from django.db import models
from modelcluster.fields import ParentalKey
from streams.blocks import (
    BookPurchaseLinkBlock,
    PDFDownloadBlock,
    CTABlock,
)
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.core.blocks import (
    RichTextBlock,
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index


class PublicationListPage(BasicPageAbstract, Page):
    """Publication list page"""

    def featured_publications_list(self):
        featured_publications = []
        for item in self.featured_publications.prefetch_related(
            'publication_page',
            'publication_page__topics',
        ).all()[:4]:
            featured_publications.append(item.publication_page)
        return featured_publications

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = ['publications.PublicationPage', 'publications.PublicationTypePage']
    templates = 'publications/publication_list_page.html'

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.hero_link_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
        MultiFieldPanel(
            [
                InlinePanel(
                    'featured_publications',
                    max_num=4,
                    min_num=0,
                    label='Publication',
                ),
            ],
            heading='Featured Publications',
            classname='collapsible collapsed',
        ),
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields

    class Meta:
        verbose_name = 'Publication List Page'


class PublicationListPageFeaturedPublication(Orderable):
    publication_list_page = ParentalKey(
        'publications.PublicationListPage',
        related_name='featured_publications',
    )
    publication_page = models.ForeignKey(
        'publications.PublicationPage',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Publication',
    )

    panels = [
        PageChooserPanel(
            'publication_page',
            ['publications.PublicationPage'],
        ),
    ]


class PublicationPage(
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    FromTheArchivesPageAbstract,
    ShareablePageAbstract,
):
    """View publication page"""

    class BookFormats(models.TextChoices):
        HARDCOVER = ('HC', 'Hardcover')
        PAPERBACK = ('PB', 'Paperback')
        TRADE_PB = ('TP', 'Trade PB')

    class PublicationTypes(models.TextChoices):
        BOOKS = ('books', 'Books')
        CIGI_COMMENTARIES = ('cigi_commentaries', 'CIGI Commentaries')
        CIGI_PAPERS = ('cigi_papers', 'CIGI Papers')
        COLLECTED_SERIES = ('collected_series', 'Collected Series')
        CONFERENCE_REPORTS = ('conference_reports', 'Conference Reports')
        ESSAY_SERIES = ('essay_series', 'Essay Series')
        POLICY_BRIEFS = ('policy_briefs', 'Policy Briefs')
        POLICY_MEMOS = ('policy_memos', 'Policy Memos')
        SPECIAL_REPORTS = ('special_reports', 'Special Reports')
        SPEECHES = ('speeches', 'Speeches')
        STUDENT_ESSAY = ('student_essay', 'Student Essay')

    book_excerpt = RichTextField(
        blank=True,
        features=['bold', 'italic', 'link'],
        verbose_name='Excerpt',
    )
    book_excerpt_download = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Excerpt Download',
    )
    book_format = models.CharField(
        blank=True,
        max_length=2,
        choices=BookFormats.choices,
        verbose_name='Format',
        help_text='Select the formation of this book/publication.',
    )
    book_pages = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Pages',
        help_text='Enter the number of pages in the book.',
    )
    book_publisher = models.CharField(blank=True, max_length=255)
    book_publisher_url = models.URLField(blank=True)
    book_purchase_links = StreamField(
        [
            ('purchase_link', BookPurchaseLinkBlock())
        ],
        blank=True,
    )
    ctas = StreamField(
        [
            ('ctas', CTABlock())
        ],
        blank=True,
        verbose_name='Call to Action Buttons',
    )
    editorial_reviews = StreamField(
        [
            ('editorial_review', RichTextBlock(
                features=['bold', 'italic', 'link'],
            )),
        ],
        blank=True,
    )
    embed_issuu = models.URLField(
        blank=True,
        verbose_name='Issuu Embed',
        help_text='Enter the Issuu URL (https://issuu.com/cigi/docs/modern_conflict_and_ai_web) to add an embedded Issuu document.',
    )
    embed_youtube = models.URLField(
        blank=True,
        verbose_name='YouTube Embed',
        help_text='Enter the YouTube URL (https://www.youtube.com/watch?v=4-Xkn1U1DkA) or short URL (https://youtu.be/o5acQ2GxKbQ) to add an embedded video.',
    )
    image_cover = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Cover image',
        help_text='An image of the cover of the publication.',
    )
    image_poster = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Poster image',
        help_text='A poster image which will be used in the highlights section of the homepage.',
    )
    isbn = models.CharField(
        blank=True,
        max_length=32,
        verbose_name='ISBN',
        help_text='Enter the print ISBN for this book.',
    )
    isbn_ebook = models.CharField(
        blank=True,
        max_length=32,
        verbose_name='eBook ISBN',
        help_text='Enter the ISBN for the eBook version of this publication.',
    )
    isbn_hardcover = models.CharField(
        blank=True,
        max_length=32,
        verbose_name='Hardcover ISBN',
        help_text='Enter the ISBN for the hardcover version of this publication.',
    )
    pdf_downloads = StreamField(
        [
            ('pdf_download', PDFDownloadBlock())
        ],
        blank=True,
        verbose_name='PDF Downloads',
    )
    publication_series = models.ForeignKey(
        'publications.PublicationSeriesPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    publication_type = models.ForeignKey(
        'publications.PublicationTypePage',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='publications',
    )
    short_description = RichTextField(
        blank=True,
        null=False,
        features=['bold', 'italic', 'link'],
    )

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    def featured_person_list(self):
        """
        For featured publications, only display the first 3 authors/editors.
        """

        # @todo test
        person_list = list(self.authors.all()) + list(self.editors.all())
        del person_list[3:]
        result = []
        for person in person_list:
            if person.author:
                result.append(person.author)
            elif person.editor:
                result.append(person.editor)
        return result

    def featured_person_list_has_more(self):
        """
        If there are more than 3 authors/editors for featured publications,
        display "and more".
        """

        # @todo test
        return (self.author_count + self.editor_count) > 3

    def has_book_metadata(self):
        return (
            self.publication_type and
            self.publication_type.title == 'Books' and
            (self.book_format or self.book_pages or self.book_publisher or self.isbn or self.isbn_ebook or self.isbn_hardcover)
        )

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
                PageChooserPanel(
                    'publication_type',
                    ['publications.PublicationTypePage'],
                ),
                FieldPanel('publishing_date'),
            ],
            heading='General Information',
            classname='collapsible',
        ),
        ContentPage.authors_panel,
        ContentPage.editors_panel,
        MultiFieldPanel(
            [
                FieldPanel('book_publisher'),
                FieldPanel('book_publisher_url'),
                FieldPanel('book_format'),
                FieldPanel('isbn'),
                FieldPanel('isbn_hardcover'),
                FieldPanel('isbn_ebook'),
                FieldPanel('book_pages'),
                StreamFieldPanel('book_purchase_links'),
                DocumentChooserPanel('book_excerpt_download'),
                FieldPanel('book_excerpt'),
            ],
            heading='Book Info',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('editorial_reviews'),
            ],
            heading='Editorial Reviews',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel('image_cover'),
                ImageChooserPanel('image_poster'),
            ],
            heading='Images',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('embed_issuu'),
                StreamFieldPanel('pdf_downloads'),
                StreamFieldPanel('ctas'),
                FieldPanel('embed_youtube'),
            ],
            heading='Media',
            classname='collapsible collapsed',
        ),
        ContentPage.recommended_panel,
        MultiFieldPanel(
            [
                FieldPanel('topics'),
                PageChooserPanel(
                    'publication_series',
                    ['publications.PublicationSeriesPage'],
                ),
                FieldPanel('projects'),
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

    search_fields = BasicPageAbstract.search_fields \
        + ContentPage.search_fields \
        + [
            index.FilterField('publication_series'),
            index.FilterField('publication_type'),
            index.FilterField('publishing_date'),
        ]

    parent_page_types = ['publications.PublicationListPage']
    subpage_types = []
    templates = 'publications/publication_page.html'

    class Meta:
        verbose_name = 'Publication'
        verbose_name_plural = 'Publications'


class PublicationTypePage(BasicPageAbstract, Page):
    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_taxonomy_id = models.IntegerField(blank=True, null=True)

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields

    parent_page_types = ['publications.PublicationListPage']
    subpage_types = []
    templates = 'publications/publication_type_page.html'

    class Meta:
        verbose_name = 'Publication Type'
        verbose_name_plural = 'Publication Types'


class PublicationSeriesListPage(BasicPageAbstract, Page):
    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = ['publications.PublicationSeriesPage']
    templates = 'publications/publication_series_list_page.html'

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
        verbose_name = 'Publication Series List Page'


class PublicationSeriesPage(
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
):
    # Reference field for Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        MultiFieldPanel(
            [
                FieldPanel('publishing_date'),
            ],
            heading='General Information',
            classname='collapsible',
        ),
        BasicPageAbstract.images_panel,
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
        SearchablePageAbstract.search_panel,
    ]

    search_fields = ContentPage.search_fields + BasicPageAbstract.search_fields

    parent_page_types = ['publications.PublicationSeriesListPage']
    subpage_types = []
    templates = 'publications/publication_series_page.html'

    class Meta:
        verbose_name = 'Publication Series'
        verbose_name_plural = 'Publication Series'
