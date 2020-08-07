from core.models import (
    BasicPageAbstract,
    FeatureablePageAbstract,
    PublishablePageAbstract,
    ShareablePageAbstract,
)
from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel


class ResearchActivityListPage(Page):
    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = ['research.ResearchActivityPage']
    templates = 'research/research_activity_list_page.html'

    class Meta:
        verbose_name = 'Research Activity List Page'


class ResearchActivityPage(
    BasicPageAbstract,
    FeatureablePageAbstract,
    PublishablePageAbstract,
    ShareablePageAbstract,
):
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
                ImageChooserPanel('image_hero'),
            ],
            heading='Images',
            classname='collapsible collapsed',
        ),
    ]

    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        ShareablePageAbstract.social_panel,
    ]

    parent_page_types = ['research.ResearchActivityListPage']
    subpage_types = []
    templates = 'research/research_activity_page.html'

    class Meta:
        verbose_name = 'Research Activity'
        verbose_name_plural = 'Research Activities'


class TopicListPage(Page):
    """Topic list page"""

    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = ['research.TopicPage']
    templates = 'research/topic_list_page.html'

    class Meta:
        verbose_name = 'Topic List Page'


class TopicPage(Page):
    """View topic page"""

    class ArchiveStatus(models.IntegerChoices):
        UNARCHIVED = (0, 'No')
        ARCHIVED = (1, 'Yes')

    description = RichTextField(blank=True, null=False, features=['h2', 'h3', 'h4', 'hr', 'ol', 'ul', 'bold', 'italic', 'link'])
    archive = models.IntegerField(choices=ArchiveStatus.choices, default=ArchiveStatus.UNARCHIVED)

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_taxonomy_id = models.IntegerField(blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('description')
    ]
    settings_panels = Page.settings_panels + [
        FieldPanel('archive')
    ]

    parent_page_types = ['research.TopicListPage']
    subpage_types = []
    templates = 'research/topic_page.html'

    class Meta:
        verbose_name = 'Topic Page'
        verbose_name_plural = 'Topic Pages'
