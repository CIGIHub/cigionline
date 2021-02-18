from django.db import models
from wagtail.core.models import Page
from core.models import BasicPageAbstract


class SubscribePage(
    Page,
    BasicPageAbstract,
):
    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
    ]

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = []
    template = 'subscribe/subscribe_page.html'

    class Meta:
        verbose_name = 'Subscribe'
