from core.models import BasicPageAbstract
from streams.blocks import ResourceBlock
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
)
from wagtail.fields import StreamField
from wagtail.models import Page


class PortalHomePage(Page, BasicPageAbstract):
    def get_template(self, request, *args, **kwargs):
        return "portal/portal_home_page.html"

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
    ]

    max_count = 1
    subpage_types = ['portal.PortalPage']

    class Meta:
        verbose_name = "Portal Home Page"


class PortalPage(Page, BasicPageAbstract):
    resources = StreamField(
        [
            ('resource', ResourceBlock()),
        ],
        blank=True,
    )

    def get_template(self, request, *args, **kwargs):
        return "portal/portal_page.html"

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        MultiFieldPanel(
            [
                FieldPanel('resources'),
            ],
            heading="Resources",
        ),
    ]

    parent_page_types = ['portal.PortalHomePage']

    class Meta:
        verbose_name = "Portal Page"
