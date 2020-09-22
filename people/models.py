from core.models import ArchiveablePageAbstract, BasicPageAbstract
from django.contrib.postgres.lookups import Unaccent
from django.db import models
from django.db.models.functions import Lower
from modelcluster.fields import ParentalManyToManyField
from streams.blocks import ParagraphBlock
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel


class PeoplePage(Page):
    """
    A special singleton page that isn't published, but is the parent to all the
    person pages at the path /people.
    """
    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = ['people.PersonPage']
    templates = 'people/person_list_page.html'

    class Meta:
        verbose_name = 'Person List Page'
        verbose_name_plural = 'Person List Pages'


class PersonListPage(BasicPageAbstract, Page):
    """
    The pages that show people. There are currently 2 on our website:
    /experts and /about/staff. This was made into a separate page model so that
    PersonPage's could not be created as children of these paths.
    """

    class PersonListPageType(models.IntegerChoices):
        DEFAULT = 0
        EXPERTS = 1
        STAFF = 2
        LEADERSHIP = 3

    person_list_page_type = models.IntegerField(choices=PersonListPageType.choices, default=PersonListPageType.DEFAULT)

    max_count = 3
    parent_page_types = ['core.BasicPage', 'core.HomePage']
    subpage_types = []
    templates = 'people/person_list_page.html'

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    def get_context(self, request):
        context = super().get_context(request)

        people = []
        if self.person_list_page_type == PersonListPage.PersonListPageType.EXPERTS:
            people = PersonPage.objects.live().filter(
                archive=ArchiveablePageAbstract.ArchiveStatus.UNARCHIVED,
                person_types__name__in=['CIGI Chair', 'Expert'],
            ).order_by(Unaccent(Lower('last_name')), Unaccent(Lower('first_name')))
        elif self.person_list_page_type == PersonListPage.PersonListPageType.STAFF:
            letter = request.GET.get('letter')
            if letter:
                letter = letter[0:1]
                people = PersonPage.objects.live().filter(
                    archive=ArchiveablePageAbstract.ArchiveStatus.UNARCHIVED,
                    last_name__istartswith=letter,
                    person_types__name='Staff',
                ).order_by(Unaccent(Lower('last_name')), Unaccent(Lower('first_name')))
            else:
                people = PersonPage.objects.live().filter(
                    archive=ArchiveablePageAbstract.ArchiveStatus.UNARCHIVED,
                    person_types__name='Staff',
                ).order_by(Unaccent(Lower('last_name')), Unaccent(Lower('first_name')))
        elif self.person_list_page_type == PersonListPage.PersonListPageType.LEADERSHIP:
            show = request.GET.get('show')
            if show == 'senior-management':
                people = PersonPage.objects.live().filter(
                    archive=ArchiveablePageAbstract.ArchiveStatus.UNARCHIVED,
                    person_types__name='Management Team',
                ).order_by(Unaccent(Lower('last_name')), Unaccent(Lower('first_name')))
            else:
                people = PersonPage.objects.live().filter(
                    archive=ArchiveablePageAbstract.ArchiveStatus.UNARCHIVED,
                    person_types__name='Board Member',
                ).order_by(Unaccent(Lower('last_name')), Unaccent(Lower('first_name')))
        context['people'] = people

        return context

    def get_template(self, request, *args, **kwargs):
        original_template = super(PersonListPage, self).get_template(request, *args, **kwargs)
        if self.person_list_page_type == PersonListPage.PersonListPageType.EXPERTS:
            return 'people/person_list_experts_page.html'
        elif self.person_list_page_type == PersonListPage.PersonListPageType.STAFF:
            return 'people/person_list_staff_page.html'
        elif self.person_list_page_type == PersonListPage.PersonListPageType.LEADERSHIP:
            return 'people/person_list_leadership_page.html'
        return original_template

    class Meta:
        verbose_name = 'Person List Page'
        verbose_name_plural = 'Person List Pages'


class PersonPage(ArchiveablePageAbstract, Page):
    """View person page"""

    class ExternalPublicationTypes(models.TextChoices):
        GENERIC = 'Generic'
        BOOK = 'Book'
        BOOK_SECTION = 'Book Section'
        EDITED_BOOK = 'Edited Book'
        ELECTRONIC_ARTICLE = 'Electronic Article'
        ELECTRONIC_BOOK = 'Electronic Book'
        JOURNAL_ARTICLE = 'Journal Article'
        NEWSPAPER_ARTICLE = 'Newspaper Article'
        REPORT = 'Report'
        THESIS = 'Thesis'
        WEB_PAGE = 'Web Page'

    address_city = models.CharField(blank=True, max_length=255)
    address_country = models.CharField(blank=True, max_length=255)
    address_line1 = models.CharField(blank=True, max_length=255)
    address_line2 = models.CharField(blank=True, max_length=255)
    address_postal_code = models.CharField(blank=True, max_length=32)
    address_province = models.CharField(blank=True, max_length=255)
    board_position = models.CharField(blank=True, max_length=255)
    body = StreamField(
        [
            ('paragraph', ParagraphBlock())
        ],
        blank=True,
        verbose_name='Full Biography'
    )
    curriculum_vitae = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    education = StreamField([
        ('education', blocks.StructBlock([
            ('degree', blocks.CharBlock(required=True)),
            ('school', blocks.CharBlock(required=True)),
            ('school_website', blocks.URLBlock(required=False)),
            ('year', blocks.IntegerBlock(required=False))
        ]))
    ], blank=True)
    email = models.EmailField(blank=True)
    expertise = StreamField([
        ('expertise', blocks.CharBlock(required=True))
    ], blank=True)
    first_name = models.CharField(blank=True, max_length=255)
    image_media = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Media photo',
        help_text='A high resolution image that is downloadable from the expert\'s page.'
    )
    image_square = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Square image',
        help_text='For circular profile images that are used throughout the website.'
    )
    languages = StreamField([
        ('language', blocks.CharBlock(required=True))
    ], blank=True)
    last_name = models.CharField(blank=True, max_length=255)
    linkedin_url = models.URLField(blank=True)
    person_types = ParentalManyToManyField('people.PersonType', blank=True)
    phone_number = models.CharField(blank=True, max_length=32)
    position = models.CharField(blank=True, max_length=255)
    projects = ParentalManyToManyField('research.ProjectPage', blank=True)
    short_bio = RichTextField(blank=True, verbose_name='Short Biography')
    external_publications = StreamField([
        ('external_publication', blocks.StructBlock([
            ('author', blocks.CharBlock(required=True)),
            ('location_in_work', blocks.CharBlock(required=False)),
            ('publisher_info', blocks.CharBlock(required=False)),
            ('publication_type', blocks.ChoiceBlock(
                required=True,
                choices=ExternalPublicationTypes.choices,
            )),
            ('secondary_author', blocks.CharBlock(required=False)),
            ('secondary_title', blocks.CharBlock(required=False)),
            ('title', blocks.CharBlock(required=False)),
            ('url', blocks.URLBlock(required=False)),
            ('url_title', blocks.CharBlock(required=False)),
            ('year', blocks.IntegerBlock(required=False))
        ]))
    ], blank=True)
    topics = ParentalManyToManyField('research.TopicPage', blank=True)
    twitter_username = models.CharField(blank=True, max_length=255)
    website = models.URLField(blank=True)

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('first_name'),
                FieldPanel('last_name'),
                FieldPanel('position'),
                FieldPanel('board_position')
            ],
            heading='General Information',
            classname='collapsible'
        ),
        MultiFieldPanel(
            [
                FieldPanel('short_bio'),
                StreamFieldPanel('body')
            ],
            heading='Biography',
            classname='collapsible collapsed'
        ),
        MultiFieldPanel(
            [
                FieldPanel('address_line1'),
                FieldPanel('address_line2'),
                FieldPanel('address_city'),
                FieldPanel('address_province'),
                FieldPanel('address_postal_code'),
                FieldPanel('address_country')
            ],
            heading='Address',
            classname='collapsible collapsed'
        ),
        MultiFieldPanel(
            [
                FieldPanel('email'),
                FieldPanel('phone_number'),
                FieldPanel('twitter_username'),
                FieldPanel('linkedin_url'),
                FieldPanel('website')
            ],
            heading='Contact Information',
            classname='collapsible collapsed'
        ),
        MultiFieldPanel(
            [
                FieldPanel('person_types'),
                StreamFieldPanel('languages'),
                DocumentChooserPanel('curriculum_vitae')
            ],
            heading='Additional Information',
            classname='collapsible collapsed'
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('education')
            ],
            heading='Education',
            classname='collapsible collapsed'
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('expertise'),
                FieldPanel('projects'),
            ],
            heading='Expertise',
            classname='collapsible collapsed'
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel('image_square'),
                ImageChooserPanel('image_media')
            ],
            heading='Images',
            classname='collapsible collapsed'
        ),
        MultiFieldPanel(
            [
                FieldPanel('topics')
            ],
            heading='Related',
            classname='collapsible collapsed'
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('external_publications')
            ],
            heading='External Publications',
            classname='collapsible collapsed'
        ),
    ]
    settings_panels = Page.settings_panels + [
        ArchiveablePageAbstract.archive_panel,
    ]

    parent_page_types = ['people.PeoplePage']
    subpage_types = []
    templates = 'people/person_page.html'

    class Meta:
        verbose_name = 'Person Page'
        verbose_name_plural = 'Person Pages'


class PersonType(models.Model):
    """
    A Django model that stores the person types. This isn't allowed to be
    edited in the admin interface. To insert/remove data - a migration needs to
    be created.

    The available person types are:
    - Board Member
    - CIGI Chair
    - Commission
    - Expert
    - External profile
    - G20 Expert
    - Management Team
    - Media Contact
    - Person
    - Program Director
    - Program Manager
    - Research Advisor
    - Research Associate
    - Research Fellow
    - Speaker
    - Staff
    """
    name = models.CharField(max_length=255)

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_taxonomy_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name
