from core.models import (
    ArchiveablePageAbstract,
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    SearchablePageAbstract,
    ShareablePageAbstract,
)
from django.db import models
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.api import APIField
from wagtail.core.blocks import (
    CharBlock,
    DateBlock,
    PageChooserBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    URLBlock,
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index


class ProjectListPage(Page):
    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = ['research.ProjectPage']
    templates = 'research/project_list_page.html'

    class Meta:
        verbose_name = 'Project List Page'


class ProjectPage(
    ArchiveablePageAbstract,
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    ShareablePageAbstract,
):
    body = StreamField(
        BasicPageAbstract.body_default_blocks + [
            BasicPageAbstract.body_poster_block,
            BasicPageAbstract.body_recommended_block,
            BasicPageAbstract.body_text_border_block,
            ('igc_timeline', StructBlock([
                ('date', CharBlock(required=True)),
                ('title', CharBlock(required=False)),
                ('body', RichTextBlock(
                    features=['bold', 'italic', 'link'],
                    required=False,
                )),
                ('location', CharBlock(required=False)),
                ('countries_represented', ImageChooserBlock(required=False)),
                ('outcomes', StreamBlock(
                    [
                        ('outcome', StructBlock([
                            ('date', DateBlock(required=False)),
                            ('text', RichTextBlock(
                                features=['bold', 'italic', 'link'],
                                required=False,
                            )),
                        ])),
                    ],
                    required=False,
                )),
                ('witnesses', StreamBlock(
                    [
                        ('witness_date', StructBlock([
                            ('date', DateBlock(required=False)),
                            ('witnesses', StreamBlock(
                                [
                                    ('witnesses_full_session', StructBlock([
                                        ('title', CharBlock(required=False)),
                                        ('witness_transcript', URLBlock(required=False)),
                                        ('witness_video', URLBlock(required=False)),
                                    ])),
                                    ('witness', StructBlock([
                                        ('name', CharBlock(required=False)),
                                        ('title', CharBlock(required=False)),
                                        ('witness_transcript', URLBlock(required=False)),
                                        ('witness_video', URLBlock(required=False)),
                                    ])),
                                ],
                            )),
                        ])),
                    ],
                    required=False,
                )),
            ])),
        ],
        blank=True,
    )
    project_contacts = StreamField(
        [
            ('contact', PageChooserBlock(required=True, page_type='people.PersonPage')),
        ],
        blank=True,
    )
    project_leads = StreamField(
        [
            ('project_lead', PageChooserBlock(required=True, page_type='people.PersonPage')),
            ('external_project_lead', CharBlock(required=True)),
        ],
        blank=True,
    )
    project_members = StreamField(
        [
            ('project_member', PageChooserBlock(required=True, page_type='people.PersonPage')),
            ('external_project_member', CharBlock(required=True)),
        ],
        blank=True,
    )
    project_types = ParentalManyToManyField('research.ProjectType', blank=True)
    related_files = StreamField(
        [
            ('file', DocumentChooserBlock()),
        ],
        blank=True,
    )

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        MultiFieldPanel(
            [
                FieldPanel('publishing_date'),
                FieldPanel('project_types'),
            ],
            heading='General Information',
            classname='collapsible',
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('project_leads'),
                StreamFieldPanel('project_members'),
                StreamFieldPanel('project_contacts'),
            ],
            heading='People',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel('image_hero'),
            ],
            heading='Images',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('topics'),
                StreamFieldPanel('related_files'),
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
        ArchiveablePageAbstract.archive_panel,
    ]

    parent_page_types = ['core.BasicPage', 'research.ProjectListPage']
    subpage_types = []
    templates = 'research/project_page.html'

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'


class ProjectType(index.Indexed, models.Model):
    """
    A Django model that stores the project types. This isn't allowed to be
    edited in the admin interface. To insert/remove data - a migration needs to
    be created.
    """
    name = models.CharField(max_length=255)

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_taxonomy_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class ResearchLandingPage(BasicPageAbstract, Page):
    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = []
    templates = 'research/research_landing_page.html'

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    class Meta:
        verbose_name = 'Research Landing Page'


class TopicListPage(Page):
    """Topic list page"""

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = ['research.TopicPage']
    templates = 'research/topic_list_page.html'

    class Meta:
        verbose_name = 'Topic List Page'


class TopicPage(ArchiveablePageAbstract, Page):
    """View topic page"""
    description = RichTextField(blank=True, null=False, features=['h2', 'h3', 'h4', 'hr', 'ol', 'ul', 'bold', 'italic', 'link'])

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_taxonomy_id = models.IntegerField(blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('description')
    ]
    settings_panels = Page.settings_panels + [
        ArchiveablePageAbstract.archive_panel,
    ]

    search_fields = Page.search_fields + [
        index.FilterField('archive'),
    ]

    api_fields = [
        APIField('title'),
        APIField('url'),
    ]

    parent_page_types = ['research.TopicListPage']
    subpage_types = []
    templates = 'research/topic_page.html'

    class Meta:
        verbose_name = 'Topic Page'
        verbose_name_plural = 'Topic Pages'
