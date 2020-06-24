from core.models import (
    BasicPageAbstract,
    FeatureablePageAbstract,
    ShareablePageAbstract,
)
from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.core.models import Page


class EventListPage(BasicPageAbstract):
    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = ['events.EventPage']
    templates = 'events/event_list_page.html'

    class Meta:
        verbose_name = 'Event List Page'


class EventPage(
    BasicPageAbstract,
    FeatureablePageAbstract,
    ShareablePageAbstract,
):
    location_address1 = models.CharField(blank=True, max_length=255, verbose_name='Address (Line 1)')
    location_address2 = models.CharField(blank=True, max_length=255, verbose_name='Address (Line 2)')
    location_city = models.CharField(blank=True, max_length=255, verbose_name='City')
    location_country = models.CharField(blank=True, max_length=255, verbose_name='Country')
    location_name = models.CharField(blank=True, max_length=255)
    location_postal_code = models.CharField(blank=True, max_length=32, verbose_name='Postal Code')
    location_province = models.CharField(blank=True, max_length=255, verbose_name='Province/State')

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
        MultiFieldPanel(
            [
                FieldPanel('location_name'),
                FieldPanel('location_address1'),
                FieldPanel('location_address2'),
                FieldPanel('location_city'),
                FieldPanel('location_province'),
                FieldPanel('location_postal_code'),
                FieldPanel('location_country'),
            ],
            heading='Location',
            classname='collapsible collapsed',
        )
    ]
    promote_panels = Page.promote_panels \
        + FeatureablePageAbstract.featureable_promote_panels \
        + ShareablePageAbstract.shareable_promote_panels

    parent_page_types = ['events.EventListPage']
    subpage_types = []
    templates = 'events/event_page.html'

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
