from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import PageChooserPanel, InlinePanel, FieldPanel, MultiFieldPanel
from wagtail.models import Orderable


class PublishEmailNotification(ClusterableModel):
    user = models.ForeignKey(
        'wagtailusers.userprofile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='+',
        verbose_name='User',
    )

    class StateOptions(models.TextChoices):
        FIRST_TIME = ('first_time', 'First-Time Publish')
        REPUBLISH = ('republish', 'Republish')
        BOTH = ('both', 'Both')

    class TriggerOptions(models.TextChoices):
        MANUAL = ('manual', 'Manual Publish')
        SCHEDULED = ('scheduled', 'Scheduled Publish')
        BOTH = ('both', 'Both')

    state_opt_in = models.CharField(
        max_length=25,
        default='first_time',
        choices=StateOptions.choices,
        verbose_name='Publish State Opt-In',
    )
    trigger_opt_in = models.CharField(
        max_length=25,
        default='scheduled',
        choices=TriggerOptions.choices,
        verbose_name='Publish Trigger Opt-In',
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('user'),
                FieldPanel('state_opt_in'),
                FieldPanel('trigger_opt_in'),
            ],
            heading='user',
        ),
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
