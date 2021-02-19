from django.db import models
from wagtail.core.models import Page
from core.models import BasicPageAbstract
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel


class SubscribePage(
    Page,
    BasicPageAbstract,
):
    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
    ]

    body = RichTextField(
        blank=True,
        null=False,
        features=['bold', 'italic', 'link'],
    )
    thank_you_message = RichTextField(
        blank=True,
        null=False,
        features=['bold', 'italic', 'link'],
    )
    follow_us = RichTextField(
        blank=True,
        null=False,
        features=['bold', 'italic', 'link'],
    )
    privacy_note = RichTextField(
        blank=True,
        null=False,
        features=['bold', 'italic', 'link'],
    )

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        FieldPanel('body'),
        FieldPanel('privacy_note'),
        FieldPanel('thank_you_message'),
        FieldPanel('follow_us'),
    ]

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = []
    template = 'subscribe/subscribe_page.html'

    class Meta:
        verbose_name = 'Subscribe Page'
