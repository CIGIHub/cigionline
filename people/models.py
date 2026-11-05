import logging

from bs4 import BeautifulSoup
from core.routers import RouterServeMixin
from core.models import (
    ArchiveablePageAbstract,
    BasicPageAbstract,
    HeroExpertTogglesAbstract,
    SearchablePageAbstract,
    ThemeablePageAbstract,
)
from django import forms
from django.contrib.postgres.lookups import Unaccent
from django.db import models
from django.db.models.functions import Lower
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from research.models import ProjectPage
from search.filters import (
    ParentalManyToManyFilterField,
    ParentalManyToManyFilterFieldName,
)
from streams.blocks import ParagraphBlock
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
from wagtail.snippets.models import register_snippet
import random

from .search_expert import expert_latest_activity_search, expert_latest_in_the_news_search

logger = logging.getLogger(__name__)


class PeoplePage(Page):
    """
    A special singleton page that isn't published, but is the parent to all the
    person pages at the path /people.
    """
    max_count = 2
    parent_page_types = ['home.HomePage', 'home.Think7HomePage']
    subpage_types = ['people.PersonPage']
    templates = 'people/person_list_page.html'

    class Meta:
        verbose_name = 'Person List Page'
        verbose_name_plural = 'Person List Pages'


class PersonListPage(RouterServeMixin, BasicPageAbstract, SearchablePageAbstract,
                     ThemeablePageAbstract, Page):
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

    max_count = 4
    parent_page_types = ['core.BasicPage', 'home.HomePage', 'home.Think7HomePage']
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
        # Page-level light/dark choice (BugHerd #136 follow-up: all composed
        # landings). The theme panel stays off — the legacy theme fork would
        # bypass the DS template.
        ThemeablePageAbstract.surface_panel,
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
        random_experts = PersonPage.objects.live().public().filter(id__in=random_expert_id_list)

        return random_experts

    def get_context(self, request):
        from core.heroes import _breadcrumb

        context = super().get_context(request)
        context['hero_crumbs'] = _breadcrumb(self)

        personFilter = {
            'archive': ArchiveablePageAbstract.ArchiveStatus.UNARCHIVED,
        }

        if self.person_list_page_type == PersonListPage.PersonListPageType.LEADERSHIP:
            personFilter['person_types__name'] = 'Management Team'
            context['senior_management'] = PersonPage.objects.live().filter(**personFilter).order_by('-person_weight', Unaccent(Lower('last_name')), Unaccent(Lower('first_name')))
            personFilter['person_types__name'] = 'Board Member'
            context['board_members'] = PersonPage.objects.live().filter(**personFilter).order_by('-person_weight', Unaccent(Lower('last_name')), Unaccent(Lower('first_name')))

        # The experts directory is an authored faceted-listing block now
        # (card type: Expert) — core.faceted_listing._expert_handler mirrors
        # the retired page-level router; RouterServeMixin serves its AJAX.

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
    RouterServeMixin,
    ArchiveablePageAbstract,
    HeroExpertTogglesAbstract,
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

    class DPHStatus(models.TextChoices):
        # The labels double as the DPH listing's Type facet options (BugHerd #365/#440).
        CURRENT = 'current', 'Current Cohort'
        ALUMNI = 'alumni', 'Alumni'

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
    position_secondary = models.CharField(blank=True, max_length=255)
    position_dph = models.CharField(
        blank=True,
        max_length=255,
        help_text='Digital Policy Hub Position',
        verbose_name='DPH Position',
    )
    projects = ParentalManyToManyField('research.ProjectPage', blank=True)
    additional_programs = StreamField(
        [
            ('program', blocks.PageChooserBlock(required=True))
        ],
        help_text='Additional programs to list under the "Programs" section on the expert/staff page.',
        blank=True,
    )
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
    # Machine-maintained expertise tags = the distinct active topics across this
    # person's authored content. Materialized weekly by the `update_expert_topics`
    # command (NOT computed on the fly) and read by `expert_data`. A plain M2M, not
    # Parental: no revision/cluster baggage, persists on .set(). Do NOT conflate
    # with the curated `topics` above, which editors set and which drives the
    # experts search facet (people/search.py) — this field must never clobber it.
    derived_topics = models.ManyToManyField(
        'research.TopicPage',
        blank=True,
        related_name='derived_experts',
    )
    twitter_username = models.CharField(blank=True, max_length=255)
    website = models.URLField(blank=True)
    dph_bio = RichTextField(
        blank=True,
        features=['bold', 'italic', 'underline', 'link', 'ul', 'ol'],
        verbose_name='Digital Policy Hub Biography',
        help_text='A short biography that is used on the Digital Policy Hub theme.',
    )
    # Status belongs to the person, not the term: an early leaver is Alumni while
    # the rest of their term stays current (BugHerd #365/#440).
    dph_status = models.CharField(
        blank=True,
        max_length=16,
        choices=DPHStatus.choices,
        default='',
        verbose_name='DPH Status',
        help_text='Digital Policy Hub fellows only. Leave blank if unknown.',
    )
    dph_terms = ParentalManyToManyField(
        'people.DPHTerm',
        blank=True,
        related_name='fellows',
        verbose_name='DPH Term(s)',
        help_text='Digital Policy Hub fellows only. The intake(s) this fellow belongs to.',
    )
    additional_authored_pages = StreamField(
        [
            ('page', blocks.PageChooserBlock(required=True))
        ],
        blank=True,
        help_text='Additional pages to list in the search table',
    )

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    @property
    def has_authored_content(self):
        # ES availability guard (here and in the other search-backed
        # properties): person pages must render without the search-driven
        # sections when Elasticsearch is unreachable, not 500.
        try:
            return expert_latest_activity_search(expert_id=self.id).count() > 0
        except Exception:
            logger.warning('Elasticsearch unavailable for person %s (has_authored_content)', self.pk)
            return False

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
        try:
            results = list(expert_latest_activity_search(expert_id=self.id)[:1])
        except Exception:
            logger.warning('Elasticsearch unavailable for person %s (latest_activity)', self.pk)
            return False
        return results[0] if results else False

    @property
    def latest_cigi_in_the_news(self):
        # Materialized inside the guard — the template iterates this, so a lazy
        # slice would defer the ES call past the try/except.
        try:
            # 6 fills the In the News grid (2-up x 3 rows, node 1677:92331).
            return list(expert_latest_in_the_news_search(expert_id=self.id)[:6])
        except Exception:
            logger.warning('Elasticsearch unavailable for person %s (latest_cigi_in_the_news)', self.pk)
            return []

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
    def programs_as_team_member(self):
        additional_programs = [block.value for block in self.additional_programs]
        programs = ProjectPage.objects.filter(members__member=self).order_by('-publishing_date')
        return additional_programs + list(programs)

    @property
    def is_external_profile(self):
        return self.person_types.filter(name='External profile').exists()

    #: Synthetic faceted-listing config for the "From This Expert" section —
    #: page-level (not block-authored); RouterServeMixin re-renders it for AJAX
    #: filter requests via get_context.
    def _from_this_expert_value(self):
        extra_ids = [
            block.value.specific.id
            for block in (self.additional_authored_pages or [])
            if block.block_type == 'page' and block.value
        ]
        return {
            'prefix': 'fte',
            # Image-led result cards per the More From This Expert section of
            # the expert-single design (1321:53357).
            'card_type': 'resource-visual',
            'author': self,
            'author_extra_ids': extra_ids,
            'heading': 'More From This Expert',
            'facets': ['topic', 'type', 'year'],
            'topic_label': 'Tags',
            'show_filters': True,
            'show_search': True,
        }

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        # DPH Speaker / Cohort (Fellow) single = Expert single + the DPH brand
        # chrome (charcoal header/main + green accent + green subscribe, per
        # the 1595 hub frames); modules inherit it. Speaker (15) and Digital
        # Policy Hub Fellow (17) are the DPH person types.
        is_dph = self.person_types.filter(id__in=[15, 17]).exists()
        if is_dph:
            context['header_surface'] = 'charcoal'
            context['main_surface'] = 'charcoal'
            context['main_accent_scheme'] = 'green'
            context['subscribe_scheme'] = 'green'

        if self.archive:
            return context

        from core.faceted_listing import _unaccent_name, build_listing_context

        # Expert single sections (Leadership Bio Template
        # composition — every section hides cleanly without data):
        # Select Resources bento = the person's CURATED picks, from the
        # Recommended panel (feature + up to 3 compacts). It used to auto-pull
        # the latest authored content, so it showed on every expert whether or
        # not anyone had curated it (Juode + Tia, BugHerd #211): "only include
        # this block when the expert has resources tagged". With nothing
        # curated the section drops out.
        curated = [
            row.recommended_content_page.specific for row in
            self.recommended.select_related('recommended_content_page')[:4]
            if row.recommended_content_page
            and row.recommended_content_page.live
        ]
        context['select_feature'] = curated[0] if curated else None
        context['select_compacts'] = curated[1:]
        # The From This Expert listing below still keys off authorship.
        has_authored = self.content_pages_as_author.filter(
            content_page__live=True).exists()
        # Include-config dicts for the reused module templates (their `self`).
        context['news_cfg'] = {
            'surface': 'light', 'accent': 'red', 'heading': 'In the News',
        }
        # Keypage: the Select Resources bento sits on the dark surface.
        context['bento_cfg'] = {
            'layout': 'split', 'surface': 'dark', 'accent': 'red',
            'show_header': True, 'heading': 'Select Resources',
        }
        # Tail rail (Leadership Bio Template): other live experts, A–Z like the
        # Experts Carousel's auto mode, excluding this person.
        context['experts_cfg'] = {
            'surface': 'dark', 'accent': 'red', 'heading': 'Experts',
            'cta_label': 'View All Experts', 'show_pagination': True,
            'card_slots': {'show_title': True, 'show_expertise': True},
        }
        # DPH brand palette (Kay, BugHerd #232): charcoal replaces black,
        # green accent replaces red, dark green replaces white bands.
        if is_dph:
            context['news_cfg'].update(surface='green', accent='green')
            context['bento_cfg'].update(surface='charcoal', accent='green')
            context['experts_cfg'].update(surface='charcoal', accent='green')
        # A person with NO sections of their own (no bio shell, no news, no
        # resources, no listing) puts the dark rail straight on the dark hero,
        # where it read as the person's own content (Yang, BugHerd #335). The
        # edge case takes the other colour variation (Kay/Juode): a light rail.
        # latest_cigi_in_the_news is an ES call — the `or` chain only reaches
        # it when every cheaper section is already empty. DPH keeps its own
        # palette (charcoal already breaks from the green hero). The media
        # photo opens the bio shell on its own (BugHerd #526), so it counts.
        elif not (
            self.body or self.education or self.is_external_profile
            or self.image_media
            or curated or has_authored or self.latest_cigi_in_the_news
        ):
            context['experts_cfg'].update(surface='light')
        # A Digital Policy Hub person's rail shows DPH people, not the general
        # expert roster (BugHerd #225 — Juode, on a DPH Program Speaker's page).
        # Mirrors whichever DPH type this person holds; everyone else keeps the
        # Expert roster.
        own_types = set(self.person_types.values_list('name', flat=True))
        dph_types = own_types & {'Speaker', 'Digital Policy Hub Fellow'}
        rail_types = sorted(dph_types) if dph_types else ['Expert']
        context['tail_experts'] = list(
            PersonPage.objects.live().public()
            .filter(archive=0, person_types__name__in=rail_types)
            .exclude(id=self.id)
            .distinct()
            .prefetch_related('derived_topics__program_theme')
            .order_by(*_unaccent_name())[:12]
        )
        # From This Expert — the faceted listing replaces the legacy React
        # expert-search-table. Only when there is anything to list.
        if has_authored:
            context.update(build_listing_context(
                request, self._from_this_expert_value(), page=self))
        return context

    def additional_authored_pages_json(self):
        pages = []
        for block in self.additional_authored_pages:
            if block.block_type == 'page' and block.value:
                page = block.value.specific
                pages.append({
                    'id': page.id,
                })
        return pages

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('first_name'),
                FieldPanel('last_name'),
                FieldPanel('position'),
                FieldPanel('position_secondary'),
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
                FieldPanel('additional_programs'),
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
                FieldPanel('external_publications'),
                FieldPanel('additional_authored_pages'),
            ],
            heading='Publications',
            classname='collapsible collapsed'
        ),
        MultiFieldPanel(
            [
                FieldPanel('position_dph'),
                FieldPanel('dph_status'),
                FieldPanel('dph_terms', widget=forms.CheckboxSelectMultiple),
                FieldPanel('dph_bio'),
            ],
            heading='DPH Fields',
            classname='collapsible collapsed'
        ),
        HeroExpertTogglesAbstract.hero_options_panel,
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


@register_snippet
class DPHTerm(models.Model):
    """A Digital Policy Hub intake (e.g. "Fall 2025"). CIGI manages the list
    under Snippets; fellows pick theirs in the DPH Fields panel (BugHerd #365/#440)."""
    name = models.CharField(
        max_length=64,
        unique=True,
        help_text='Season and year, e.g. "Fall 2025".',
    )
    start_date = models.DateField(
        help_text='First day of the term. Orders the Term filter, newest first.',
    )

    panels = [FieldPanel('name'), FieldPanel('start_date')]

    class Meta:
        ordering = ['-start_date', 'name']
        verbose_name = 'DPH Term'
        verbose_name_plural = 'DPH Terms'

    def __str__(self):
        return self.name


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
