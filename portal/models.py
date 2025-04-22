from core.models import BasicPageAbstract
from streams.blocks import ResourceBlock
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
)
from wagtail.fields import StreamField
from wagtail.models import Page


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

    max_count = 1

    class Meta:
        verbose_name = "Portal Page"
