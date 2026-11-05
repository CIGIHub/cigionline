from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    InlinePanel,
    FieldPanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.models import Orderable
from wagtail.search import index


class Menu(index.Indexed, ClusterableModel):
    name = models.CharField(max_length=32)
    slug = models.CharField(max_length=32)

    # Optional link under this menu's header dropdown, e.g. "Browse All
    # Archived Topics" under Topics (BugHerd #539). One per menu, so only one
    # item can sit there. Same page-or-URL precedence as MenuItem.
    bottom_link_label = models.CharField(
        blank=True,
        max_length=128,
        verbose_name='Label',
    )
    bottom_link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name='Link page',
    )
    bottom_link_url = models.CharField(
        blank=True,
        max_length=512,
        verbose_name='Link URL',
        help_text='An external URL (https://...) or an internal URL (/archived-topics/). This field is only considered if there is no link page.',
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
        MultiFieldPanel(
            [
                InlinePanel('menu_items'),
            ],
            heading='Menu Items',
        ),
        MultiFieldPanel(
            [
                FieldPanel('bottom_link_label'),
                PageChooserPanel('bottom_link_page'),
                FieldPanel('bottom_link_url'),
            ],
            heading='Bottom link',
            help_text="Shown as a full-width link under this dropdown's columns (desktop) and as the last link in this section (phones). Leave blank for none.",
        ),
    ]

    @property
    def bottom_link(self):
        """
        The dropdown's bottom link as {'label', 'page', 'url'}, or None when the
        label or link is blank. `page` wins over `url` (templates render it with
        {% pageurl %}, like menu items). A chosen page that is unpublished hides
        the link rather than falling back to the URL or linking a 404.
        """
        label = self.bottom_link_label.strip()
        if not label:
            return None
        if self.bottom_link_page_id:
            page = self.bottom_link_page
            if not page.live:
                return None
            return {'label': label, 'page': page, 'url': ''}
        url = self.bottom_link_url.strip()
        if not url:
            return None
        return {'label': label, 'page': None, 'url': url}

    @classmethod
    def get_indexed_objects(cls):
        return cls.objects.none()

    def __str__(self):
        return self.name


class MenuItem(Orderable):
    title = models.CharField(max_length=128)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.CASCADE,
    )
    link_url = models.CharField(
        blank=True,
        max_length=512,
        help_text='An external URL (https://...) or an internal URL (/interactives/2019annualreport/). This field is only considered if there is no link page.',
    )
    description = models.CharField(
        blank=True,
        max_length=255,
        help_text='Optional short blurb shown beneath this item in a mega-menu panel (header nav).',
    )
    menu = ParentalKey('Menu', related_name='menu_items', on_delete=models.CASCADE)
    submenu = models.ForeignKey(
        'menus.Menu',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.CASCADE,
        help_text='Related submenu to show in the hamburger menu.'
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('description'),
        PageChooserPanel('link_page'),
        FieldPanel('link_url'),
        FieldPanel('submenu'),
    ]
