from core.models import (
    BasicPageAbstract,
    FeatureablePageAbstract,
    PublishablePageAbstract,
    ShareablePageAbstract,
)
from django.db import models
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.core.blocks import (
    CharBlock,
    PageChooserBlock,
    RichTextBlock,
    StructBlock,
    URLBlock,
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel


class PublicationListPage(BasicPageAbstract):
    """Publication list page"""

    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = ['publications.PublicationPage']
    templates = 'publications/publication_list_page.html'

    class Meta:
        verbose_name = 'Publication List Page'


class PublicationPage(
    BasicPageAbstract,
    FeatureablePageAbstract,
    PublishablePageAbstract,
    ShareablePageAbstract,
):
    """View publication page"""

    class BookFormats(models.TextChoices):
        HARDCOVER = ('HC', 'Hardcover')
        PAPERBACK = ('PB', 'Paperback')
        TRADE_PB = ('TP', 'Trade PB')

    authors = StreamField(
        [
            ('author', PageChooserBlock(required=True, page_type='people.PersonPage')),
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
            ('pdf_download', StructBlock([
                ('file', DocumentChooserBlock(required=True)),
                ('button_text', CharBlock(
                    required=False,
                    help_text='Optional text to replace the button text. If left empty, the button will read "Download PDF".',
                )),
            ], label='PDF Download'))
        ],
        blank=True,
        verbose_name='PDF Downloads',
    )
    publication_series = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    topics = ParentalManyToManyField('research.TopicPage', blank=True)

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
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
        MultiFieldPanel(
            [
                FieldPanel('topics'),
                PageChooserPanel(
                    'publication_series',
                    ['publications.PublicationSeriesPage'],
                ),
            ],
            heading='Related',
            classname='collapsible collapsed',
        ),
    ]

    parent_page_types = ['publications.PublicationListPage']
    subpage_types = []
    templates = 'publications/publication_page.html'

    class Meta:
        verbose_name = 'Publication'
        verbose_name_plural = 'Publications'


class PublicationSeriesListPage(BasicPageAbstract):
    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = ['publications.PublicationSeriesPage']
    templates = 'publications/publication_series_list_page.html'

    class Meta:
        verbose_name = 'Publication Series List Page'


class PublicationSeriesPage(
    BasicPageAbstract,
    FeatureablePageAbstract,
    PublishablePageAbstract,
):
    topics = ParentalManyToManyField('research.TopicPage', blank=True)

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
            ],
            heading='Related',
            classname='collapsible collapsed',
        ),
    ]

    parent_page_types = ['publications.PublicationSeriesListPage']
    subpage_types = []
    templates = 'publications/publication_series_page.html'

    class Meta:
        verbose_name = 'Publication Series'
        verbose_name_plural = 'Publication Series'
