from core.models import BasicPageAbstract
from streams.blocks import BorderedContentBlock, CollapsibleParagraphBlockV2, DotDividerBlock, SectionHeadingBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.documents.blocks import DocumentChooserBlock


class PolicyPopupGroupPage(BasicPageAbstract, Page):
    """Singleton page for the Policy Pop Up Group."""

    body = StreamField(
        BasicPageAbstract.body_default_blocks + [
            ('bordered_content', BorderedContentBlock()),
            ('collapsible_paragraph_v2', CollapsibleParagraphBlockV2()),
            ('dot_divider', DotDividerBlock()),
            ('section_heading', SectionHeadingBlock()),
        ],
        blank=True,
        use_json_field=True,
    )
    related_files = StreamField(
        [
            ('file', DocumentChooserBlock()),
        ],
        blank=True,
        use_json_field=True,
    )
    footnotes = RichTextField(
        blank=True,
        features=[
            'bold',
            'endofarticle',
            'h3',
            'h4',
            'italic',
            'link',
            'ol',
            'ul',
            'subscript',
            'superscript',
            'anchor',
        ],
    )

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = []
    template = 'policy_popup/policy_popup_group_page.html'

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
        MultiFieldPanel(
            [
                FieldPanel('footnotes'),
            ],
            heading='Footnotes',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('related_files'),
            ],
            heading='Related Files',
            classname='collapsible collapsed',
        ),
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields

    class Meta:
        verbose_name = 'Policy Pop Up Group Page'
