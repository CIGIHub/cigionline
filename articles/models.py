from core.models import (
    BasicPageAbstract,
    FeatureablePageAbstract,
    PublishablePageAbstract,
    ShareablePageAbstract,
)
from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel


class ArticleLandingPage(Page):
    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = []
    templates = 'articles/article_landing_page.html'

    class Meta:
        verbose_name = 'Article Landing Page'


class ArticleListPage(Page):
    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = ['articles.ArticlePage']
    templates = 'articles/article_list_page.html'

    class Meta:
        verbose_name = 'Article List Page'


class ArticlePage(
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

    parent_page_types = ['articles.ArticleListPage']
    subpage_types = []
    templates = 'articles/article_page.html'

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
