from core.models import (
    ArchiveablePageAbstract,
    BasicPageAbstract,
    ContentPage,
    SearchablePageAbstract,
    ThemeablePageAbstract,
)
from publications.models import PublicationPage
from articles.models import ArticlePage
from django.contrib.postgres.lookups import Unaccent
from django.db import models
from django.db.models.functions import Lower
from itertools import chain
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from streams.blocks import ParagraphBlock
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.api import APIField
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
import random


class PeoplePage(Page):
    """
    A special singleton page that isn't published, but is the parent to all the
    person pages at the path /people.
    """
    max_count = 1
    parent_page_types = ['home.HomePage']
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
    parent_page_types = ['core.BasicPage', 'home.HomePage']
    subpage_types = []
    templates = 'people/person_list_page.html'

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.hero_link_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    def featured_experts_random(self):
        filters = {
            'authors__author__person_types': 4,
            'authors__author__archive': 0,
            'publishing_date__isnull': False,
        }
        Q = models.Q
        publications_ids = PublicationPage.objects.live().public().filter(**filters).distinct().values_list('id', flat=True)
        articles_ids = ArticlePage.objects.live().public().filter(**filters, article_type__in=['cigi_in_the_news', 'op_ed', 'opinion']).distinct().values_list('id', flat=True)
        all_ids = list(chain(publications_ids, articles_ids))
        random_ids = random.sample(all_ids, min(len(all_ids), 6))

        random_content = ContentPage.objects.filter(id__in=random_ids)

        return random_content

    def get_context(self, request):
        context = super().get_context(request)

        personFilter = {
            'archive': ArchiveablePageAbstract.ArchiveStatus.UNARCHIVED,
        }

        if self.person_list_page_type == PersonListPage.PersonListPageType.EXPERTS:
            personFilter['person_types__name__in'] = ['CIGI Chair', 'Expert']
            context['people'] = PersonPage.objects.live().filter(**personFilter).order_by(Unaccent(Lower('last_name')), Unaccent(Lower('first_name')))
        elif self.person_list_page_type == PersonListPage.PersonListPageType.STAFF:
            personFilter['person_types__name'] = 'Staff'
            letter = request.GET.get('letter')
            if letter:
                letter = letter[0:1]
                personFilter['last_name__istartswith'] = letter
            context['people'] = PersonPage.objects.live().filter(**personFilter).order_by(Unaccent(Lower('last_name')), Unaccent(Lower('first_name')))
        elif self.person_list_page_type == PersonListPage.PersonListPageType.LEADERSHIP:
            personFilter['person_types__name'] = 'Management Team'
            context['senior_management'] = PersonPage.objects.live().filter(**personFilter).order_by('-person_weight', Unaccent(Lower('last_name')), Unaccent(Lower('first_name')))
            personFilter['person_types__name'] = 'Board Member'
            context['board_members'] = PersonPage.objects.live().filter(**personFilter).order_by('-person_weight', Unaccent(Lower('last_name')), Unaccent(Lower('first_name')))

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


class PersonPage(
    ArchiveablePageAbstract,
    Page,
    SearchablePageAbstract,
    ThemeablePageAbstract,
):
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
    byline = RichTextField(blank=True, features=['bold', 'italic', 'link'],)
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
    person_weight = models.IntegerField(blank=False, null=False, default=0)
    phone_number = models.CharField(blank=True, max_length=32)
    position = models.CharField(blank=True, max_length=255)
    projects = ParentalManyToManyField('research.ProjectPage', blank=True)
    short_bio = RichTextField(
        blank=True,
        features=['bold', 'italic', 'link'],
        verbose_name='Short Biography',
    )
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

    def latest_activity(self):
        # @todo test
        content_pages_as_author = self.content_pages_as_author.filter(content_page__live=True).values('content_page_id', 'content_page__publishing_date')
        content_pages_as_editor = self.content_pages_as_editor.filter(content_page__live=True).values('content_page_id', 'content_page__publishing_date')
        latest_activity = content_pages_as_author.union(content_pages_as_editor).order_by('-content_page__publishing_date').first()
        if latest_activity:
            content_page = ContentPage.objects.get(pk=latest_activity.get('content_page_id'))
            if content_page:
                return content_page.specific
        return False

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
                StreamFieldPanel('body'),
                FieldPanel('byline'),
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
                DocumentChooserPanel('curriculum_vitae'),
                FieldPanel('person_weight'),
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
                InlinePanel('recommended'),
            ],
            heading='Recommended',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('external_publications')
            ],
            heading='External Publications',
            classname='collapsible collapsed'
        ),
    ]

    promote_panels = Page.promote_panels + [
        SearchablePageAbstract.search_panel,
    ]

    settings_panels = Page.settings_panels + [
        ArchiveablePageAbstract.archive_panel,
        ThemeablePageAbstract.theme_panel,
    ]

    api_fields = [
        APIField('title'),
        APIField('url'),
    ]

    parent_page_types = ['people.PeoplePage']
    subpage_types = []
    templates = 'people/person_page.html'

    class Meta:
        verbose_name = 'Person Page'
        verbose_name_plural = 'Person Pages'


class PersonPageRecommendedContent(Orderable):
    person_page = ParentalKey(
        'people.PersonPage',
        related_name='recommended',
    )
    recommended_content_page = models.ForeignKey(
        'wagtailcore.Page',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Recommended Content',
    )

    panels = [
        PageChooserPanel(
            'recommended_content_page',
            ['wagtailcore.Page'],
        )
    ]


class PersonType(index.Indexed, models.Model):
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
