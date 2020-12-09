from core.models import (
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    SearchablePageAbstract,
    ShareablePageAbstract,
)
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from streams.blocks import AuthorBlock, PDFDownloadBlock
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.api import APIField
from wagtail.core.blocks import (
    CharBlock,
    PageChooserBlock,
    RichTextBlock,
    StructBlock,
    URLBlock,
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel


class PublicationListPage(BasicPageAbstract, Page):
    """Publication list page"""

    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = ['publications.PublicationPage']
    templates = 'publications/publication_list_page.html'

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
        MultiFieldPanel(
            [
                InlinePanel(
                    'featured_publications',
                    max_num=4,
                    min_num=4,
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

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        all_publications = PublicationPage.objects.live().public().order_by('-publishing_date')
        paginator = Paginator(all_publications, 24)
        page = request.GET.get('page')
        try:
            publications = paginator.page(page)
        except PageNotAnInteger:
            publications = paginator.page(1)
        except EmptyPage:
            publications = paginator.page(paginator.num_pages)
        context['publications'] = publications
        return context

    class Meta:
        verbose_name = 'Publication List Page'


class PublicationListPageFeaturedPublication(Orderable):
    publication_list_page = ParentalKey(
        'publications.PublicationListPage',
        related_name='featured_publications',
    )
    publication_page = models.ForeignKey(
        'wagtailcore.Page',
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
    ShareablePageAbstract,
):
    """View publication page"""

    class BookFormats(models.TextChoices):
        HARDCOVER = ('HC', 'Hardcover')
        PAPERBACK = ('PB', 'Paperback')
        TRADE_PB = ('TP', 'Trade PB')

    authors = StreamField(
        [
            ('author', AuthorBlock(required=True, page_type='people.PersonPage')),
            ('external_author', CharBlock(required=True)),
        ],
        blank=True,
    )
    book_excerpt = RichTextField(blank=True, verbose_name='Excerpt')
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
            ('purchase_link', StructBlock([
                ('link_text', CharBlock(required=True)),
                ('url', URLBlock(required=True)),
            ])),
        ],
        blank=True,
    )
    editorial_reviews = StreamField(
        [
            ('editorial_review', RichTextBlock()),
        ],
        blank=True,
    )
    editors = StreamField(
        [
            ('editor', PageChooserBlock(required=True, page_type='people.PersonPage')),
            ('external_editor', CharBlock(required=True)),
        ],
        blank=True,
    )
    embed_youtube = models.URLField(
        blank=True,
        verbose_name='YouTube Embed',
        help_text='Enter the YouTube URL (https://www.youtube.com/watch?v=4-Xkn1U1DkA) or short URL (https://youtu.be/o5acQ2GxKbQ) to add an embedded video.',
    )
    image_cover = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Cover image',
        help_text='An image of the cover of the publication.',
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
    projects = ParentalManyToManyField('research.ProjectPage', blank=True)
    publication_series = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    def featured_person_list(self):
        """
        For featured publications, only display the first 3 authors/editors.
        """

        person_list = list(self.authors) + list(self.editors)
        del person_list[3:]
        return person_list

    def featured_person_list_has_more(self):
        """
        If there are more than 3 authors/editors for featured publications,
        display "and more".
        """

        return len(list(self.authors) + list(self.editors)) > 3

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
        MultiFieldPanel(
            [
                StreamFieldPanel('authors'),
            ],
            heading='Authors',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('editors'),
            ],
            heading='Editors',
            classname='collapsible collapsed',
        ),
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
            ],
            heading='Images',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('pdf_downloads'),
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
    ]
    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        ShareablePageAbstract.social_panel,
        SearchablePageAbstract.search_panel,
    ]

    api_fields = [
        APIField('authors'),
        APIField('pdf_downloads'),
        APIField('publishing_date'),
        APIField('title'),
        APIField('topics'),
        APIField('url'),
    ]

    parent_page_types = ['publications.PublicationListPage']
    subpage_types = []
    templates = 'publications/publication_page.html'

    class Meta:
        verbose_name = 'Publication'
        verbose_name_plural = 'Publications'


class PublicationSeriesListPage(BasicPageAbstract, Page):
    max_count = 1
    parent_page_types = ['core.HomePage']
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

    class Meta:
        verbose_name = 'Publication Series List Page'


class PublicationSeriesPage(
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
):
    projects = ParentalManyToManyField('research.ProjectPage', blank=True)

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

    parent_page_types = ['publications.PublicationSeriesListPage']
    subpage_types = []
    templates = 'publications/publication_series_page.html'

    class Meta:
        verbose_name = 'Publication Series'
        verbose_name_plural = 'Publication Series'
