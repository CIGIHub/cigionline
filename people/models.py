from bs4 import BeautifulSoup
from core.models import (
    ArchiveablePageAbstract,
    BasicPageAbstract,
    SearchablePageAbstract,
    ThemeablePageAbstract,
)
from django.contrib.postgres.lookups import Unaccent
from django.db import models
from django.db.models.functions import Lower
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from search.filters import (
    ParentalManyToManyFilterField,
    ParentalManyToManyFilterFieldName,
)
from streams.blocks import ParagraphBlock, FeatureExpertRow
from unidecode import unidecode
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail import blocks
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index
import random

from .search_expert import expert_latest_activity_search, expert_latest_in_the_news_search


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


class PersonListPage(BasicPageAbstract, SearchablePageAbstract, Page):
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
    layout = StreamField([
        ('row', FeatureExpertRow()),
    ],
        blank=True,
    )

    max_count = 3
    parent_page_types = ['core.BasicPage', 'home.HomePage']
    subpage_types = []
    templates = 'people/person_list_page.html'

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.hero_link_panel,
        BasicPageAbstract.body_panel,
        MultiFieldPanel([
            FieldPanel('layout'),
        ], heading='Layout', classname='collapsible collapsed home-page-layout'),
        BasicPageAbstract.images_panel,
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields + SearchablePageAbstract.search_fields

    def featured_experts_random(self):
        expert_id_list = list(PersonPage.objects.live().public().filter(
            person_types=4,
            archive=0,
            content_pages_as_author__isnull=False,
        ).values_list('id', flat=True))
        expert_id_list = list(set(expert_id_list))
        random_expert_id_list = random.sample(expert_id_list, min(len(expert_id_list), 6))
        random_experts = PersonPage.objects.filter(id__in=random_expert_id_list)

        return random_experts

    def get_context(self, request):
        context = super().get_context(request)

        personFilter = {
            'archive': ArchiveablePageAbstract.ArchiveStatus.UNARCHIVED,
        }

        if self.person_list_page_type == PersonListPage.PersonListPageType.LEADERSHIP:
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
        verbose_name='Full Biography',
        use_json_field=True,
    )
    byline = RichTextField(blank=True, features=['bold', 'italic', 'link'],)
    curriculum_vitae = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    education = StreamField(
        [
            ('education', blocks.StructBlock([
                ('degree', blocks.CharBlock(required=True)),
                ('school', blocks.CharBlock(required=True)),
                ('school_website', blocks.URLBlock(required=False)),
                ('year', blocks.IntegerBlock(required=False))
            ]))
        ],
        blank=True,
        use_json_field=True,
    )
    email = models.EmailField(blank=True)
    expertise = StreamField(
        [
            ('expertise', blocks.CharBlock(required=True))
        ],
        blank=True,
        use_json_field=True,
    )
    first_name = models.CharField(blank=True, max_length=255)
    image_media = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Media photo',
        help_text='A high resolution image that is downloadable from the expert\'s page.'
    )
    image_square = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Square image',
        help_text='For circular profile images that are used throughout the website.'
    )
    languages = StreamField(
        [
            ('language', blocks.CharBlock(required=True))
        ],
        blank=True,
        use_json_field=True,
    )
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
    external_publications = StreamField(
        [
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
        ],
        blank=True,
        use_json_field=True,
    )
    topics = ParentalManyToManyField('research.TopicPage', blank=True)
    twitter_username = models.CharField(blank=True, max_length=255)
    website = models.URLField(blank=True)

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    @property
    def has_authored_content(self):
        return expert_latest_activity_search(expert_id=self.id).count() > 0

    @property
    def first_name_lowercase(self):
        return unidecode(self.first_name.lower())

    @property
    def last_name_lowercase(self):
        return unidecode(self.last_name.lower())

    @property
    def topic_names(self):
        return [item.title for item in self.topics.all()]

    @property
    def image_square_url(self):
        if self.image_square:
            return self.image_square.get_rendition('fill-300x300').url
        return ''

    @property
    def expertise_list(self):
        expertise_list = []
        for block in self.expertise:
            if block.block_type == 'expertise':
                expertise_list.append(block.value)
        return expertise_list

    @property
    def phone_number_clean(self):
        return self.phone_number.replace('.', ' ').lower()

    @property
    def latest_activity(self):
        # @todo test
        latest_activity_query = expert_latest_activity_search(expert_id=self.id)[:2]
        if latest_activity_query.count() > 0:
            return latest_activity_query[:2]
        return False

    @property
    def latest_cigi_in_the_news(self):
        articles = expert_latest_in_the_news_search(expert_id=self.id)
        return articles[:3]

    @property
    def person_name(self):
        return self.title

    @property
    def body_snippet(self):
        snippet = ''
        for i in range(5):
            try:
                snippet = BeautifulSoup(self.body[i].value.source, "html.parser").get_text()
                break
            except AttributeError:
                continue
            except IndexError:
                break
        if self.body:
            return snippet[:350] if len(snippet) > 350 else snippet
        else:
            return snippet

    @property
    def linkedin_username(self):
        url = self.linkedin_url
        if not url or not url.startswith("https://www.linkedin.com/"):
            return None
        url = url.replace("https://www.linkedin.com/", "").rstrip("/")
        return url

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('first_name'),
                FieldPanel('last_name'),
                FieldPanel('position'),
                FieldPanel('board_position')
            ],
            heading='General Information',
            classname='collapsible collapsed'
        ),
        MultiFieldPanel(
            [
                FieldPanel('short_bio'),
                FieldPanel('body'),
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
                FieldPanel('languages'),
                FieldPanel('curriculum_vitae'),
                FieldPanel('person_weight'),
            ],
            heading='Additional Information',
            classname='collapsible collapsed'
        ),
        MultiFieldPanel(
            [
                FieldPanel('education')
            ],
            heading='Education',
            classname='collapsible collapsed'
        ),
        MultiFieldPanel(
            [
                FieldPanel('expertise'),
                FieldPanel('projects'),
            ],
            heading='Expertise',
            classname='collapsible collapsed'
        ),
        MultiFieldPanel(
            [
                FieldPanel('image_square'),
                FieldPanel('image_media')
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
                FieldPanel('external_publications')
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

    search_fields = Page.search_fields \
        + ArchiveablePageAbstract.search_fields + [
            index.SearchField('body'),
            index.FilterField('first_name_lowercase'),
            index.FilterField('last_name_lowercase'),
            index.SearchField('topic_names'),
            index.SearchField('person_name'),
            ParentalManyToManyFilterFieldName('person_types'),
            ParentalManyToManyFilterField('topics'),
        ] \
        + SearchablePageAbstract.search_fields

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
