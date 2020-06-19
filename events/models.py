from core.models import (
    BasicPageAbstract,
    FeatureablePageAbstract,
    ShareablePageAbstract,
)
from django.db import models


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
    location_address1 = models.CharField(blank=True, max_length=255)

    parent_page_types = ['events.EventListPage']
    subpage_types = []
    templates = 'events/event_page.html'

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
