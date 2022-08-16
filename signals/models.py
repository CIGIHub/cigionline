from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import PageChooserPanel, InlinePanel, FieldPanel
from wagtail.core.models import Orderable
from wagtail.snippets.models import register_snippet


@register_snippet
class PublishEmailNotification(ClusterableModel):
    user = models.ForeignKey(
        'wagtailusers.userprofile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='+',
        verbose_name='User',
    )
    panels = [
        FieldPanel('user'),
        InlinePanel('page_type_permissions'),
    ]


class PageTypePermission(Orderable):
    permission = ParentalKey(
        'signals.PublishEmailNotification',
        related_name='page_type_permissions',
    )
    page_type = models.ForeignKey(
        'wagtailcore.Page',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Page Type',
    )

    panels = [
        PageChooserPanel(
            'page_type',
            [
                'articles.ArticleListPage',
                'multimedia.MultimediaListPage',
                'events.EventListPage',
                'publications.PublicationListPage',
                'articles.ArticleSeriesListPage'
            ]
        ),
    ]
