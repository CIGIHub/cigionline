from core.models import (
    BasicPageAbstract,
    FeatureablePageAbstract,
    PublishablePageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
)
from django.db import models
from wagtail.core.models import Page


class MultimediaSeriesListPage(Page):
    """
    A singleton page that isn't published, but is the parent to all the
    multimedia series pages at the path /multimedia-series.
    """
    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = ['multimedia.MultimediaSeriesPage']
    templates = 'multimedia/multimedia_series_list_page.html'

    class Meta:
        verbose_name = 'Multimedia Series List Page'


class MultimediaSeriesPage(
    BasicPageAbstract,
    FeatureablePageAbstract,
    PublishablePageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
):
    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
    ]

    settings_panels = Page.settings_panels + [
        ThemeablePageAbstract.theme_panel,
    ]

    parent_page_types = ['core.HomePage']
    subpage_types = []
    templates = 'multimedia/multimedia_series_page.html'

    class Meta:
        verbose_name = 'Multimedia Series'
        verbose_name_plural = 'Multimedia Series'
