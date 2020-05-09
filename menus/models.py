from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import (
    InlinePanel,
    FieldPanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.core.models import Orderable


class Menu(ClusterableModel):
    name = models.CharField(max_length=32)
    slug = models.CharField(max_length=32)

    panels = [
        MultiFieldPanel(
            [
                InlinePanel('menu_items'),
            ],
            heading='Menu Items',
        ),
    ]

    def __str__(self):
        return self.name


class MenuItem(Orderable):
    title = models.CharField(max_length=32)
    link_url = models.CharField(blank=True, max_length=512)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.CASCADE,
    )
    menu = ParentalKey('Menu', related_name='menu_items', on_delete=models.CASCADE)
    submenu = models.ForeignKey(
        'menus.Menu',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.CASCADE,
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('link_url'),
        PageChooserPanel('link_page'),
        FieldPanel('submenu'),
    ]

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_url:
            return self.link_url
        return '#'
