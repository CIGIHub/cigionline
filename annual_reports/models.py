from core.models import (
    BasicPageAbstract,
    FeatureablePageAbstract,
    SearchablePageAbstract,
    ShareablePageAbstract
)
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.shortcuts import render
from streams.blocks import ARSlideBoardBlock, ARSlideChooserBlock, ARSlideColumnBlock, SPSlideBoardBlock, SPSlideChooserBlock, SPSlideFrameworkBlock
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
)
from wagtail.blocks import PageChooserBlock, RichTextBlock
from wagtail.fields import StreamField, RichTextField
from wagtail.models import Page
from wagtail.rich_text import expand_db_html
from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.models import Media
from wagtailmedia.widgets import AdminMediaChooser


class AnnualReportListPage(BasicPageAbstract, Page, SearchablePageAbstract):
    max_count = 1
    parent_page_types = ['core.BasicPage']
    subpage_types = ['annual_reports.AnnualReportPage']
    templates = 'annual_reports/annual_report_list_page.html'

    featured_reports = StreamField(
        [
            ('featured_report', PageChooserBlock(
                required=True,
                page_type=['annual_reports.AnnualReportPage'],
            )),
        ],
        blank=True,
        use_json_field=True,
    )

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.hero_link_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
        MultiFieldPanel(
            [
                FieldPanel('featured_reports'),
            ],
            heading='Featured Annual Reports',
            classname='collapsible collapsed',
        ),
    ]
    promote_panels = Page.promote_panels + [
        SearchablePageAbstract.search_panel
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]
    search_fields = Page.search_fields + BasicPageAbstract.search_fields + SearchablePageAbstract.search_fields

    class Meta:
        verbose_name = 'Annual Report List Page'


class AnnualReportPage(FeatureablePageAbstract, Page, SearchablePageAbstract):
    """View annual report page"""

    image_poster = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Cover image',
        help_text='Poster sized image that is displayed in the featured section on the Annual Reports page.',
    )
    report_english = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    report_financial = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    report_french = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    report_interactive = models.CharField(
        blank=True,
        max_length=255,
        help_text='Internal path to the interactive report. Example: /interactives/2019annualreport',
    )
    year = models.IntegerField(validators=[MinValueValidator(2005), MaxValueValidator(2050)])

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('year'),
            ],
            heading='General Information',
            classname='collapsible',
        ),
        MultiFieldPanel(
            [
                FieldPanel('report_english'),
                FieldPanel('report_french'),
                FieldPanel('report_financial'),
                FieldPanel('report_interactive'),
            ],
            heading='Reports',
            classname='collapsible',
        ),
        MultiFieldPanel(
            [
                FieldPanel('image_poster'),
            ],
            heading='Images',
            classname='collapsible collapsed',
        )
    ]
    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        SearchablePageAbstract.search_panel,
    ]

    search_fields = Page.search_fields + SearchablePageAbstract.search_fields

    parent_page_types = ['annual_reports.AnnualReportListPage']
    subpage_types = ['annual_reports.AnnualReportSPAPage']
    templates = 'annual_reports/annual_report_page.html'

    class Meta:
        verbose_name = 'Annual Report Page'
        verbose_name_plural = 'Annual Report Pages'


class AnnualReportSPAPage(FeatureablePageAbstract, SearchablePageAbstract, ShareablePageAbstract, Page):
    """View annual report SPA page"""

    slides = StreamField(
        [("slide", ARSlideChooserBlock())],
        blank=True,
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("slides"),
            ],
            heading="Slides",
            classname="collapsible",
        ),
    ]

    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        ShareablePageAbstract.social_panel,
        SearchablePageAbstract.search_panel,
    ]

    subpage_types = ["AnnualReportSlidePage"]

    def get_template(self, request, *args, **kwargs):
        return "annual_reports/annual_report_spa_page.html"


class SlidePageAbstract(models.Model):
    SLIDE_TYPES = [
        ("regular", "Regular Slide"),
        ("toc", "Table of Contents"),
        ("text", "Text Slide"),
        ("quote", "Quote Slide"),
    ]
    BACKGROUND_COLOURS = [
        ("white", "White"),
        ("black", "Black"),
    ]
    SLIDE_THEMES = [
        ("annual_report", "Annual Report"),
        ("strategic_plan", "Strategic Plan"),
    ]

    slide_title = models.CharField(max_length=255, help_text="Title of the slide")
    slide_subtitle = models.CharField(
        max_length=255,
        blank=True,
        help_text="Subtitle of the slide",
    )
    slide_content = RichTextField(blank=True, help_text="Content of the slide")
    slide_type = models.CharField(
        max_length=255,
        choices=SLIDE_TYPES,
        default="regular",
        help_text="Type of slide",
    )
    slide_theme = models.CharField(
        max_length=255,
        choices=SLIDE_THEMES,
        default="annual_report",
        help_text="Theme of the slide",
    )
    background_image = models.ForeignKey(
        "images.CigionlineImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Background image for the slide",
    )
    background_images = StreamField(
        [
            ("image", ImageChooserBlock()),
        ],
        blank=True,
        help_text="Additional background images for the slide",
    )
    background_video = models.ForeignKey(
        Media,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Background video for the slide",
    )
    background_colour = models.CharField(
        max_length=255,
        choices=BACKGROUND_COLOURS,
        blank=True,
        help_text="Background colour for the slide",
    )
    include_on_toc = models.BooleanField(
        default=True,
        help_text="Include this slide in the table of contents",
    )

    class Meta:
        abstract = True


class AnnualReportSlidePage(SlidePageAbstract, Page):
    """Each individual slide within the annual report."""

    SLIDE_TYPES = [
        ('title', 'Title'),
        ('toc', 'Table of Contents'),
        ('chairs_message', 'Chair\'s Message'),
        ('presidents_message', 'President\'s Message'),
        ('standard', 'Standard'),
        ('outputs_and_activities', 'Outputs and Activities'),
        ('timeline', 'Timeline'),
        ('financials', 'Financials'),
    ]

    slide_type = models.CharField(
        max_length=255,
        choices=SLIDE_TYPES,
        default='standard',
        help_text='Type of slide',
    )

    slide_title_fr = models.CharField(max_length=255, help_text="Title of the slide (French)", blank=True)
    year = models.PositiveIntegerField(help_text="Year of the report - only used for title page", blank=True, null=True)

    ar_slide_content = StreamField(
        [
            ("column", ARSlideColumnBlock()),
            ("board", ARSlideBoardBlock()),
        ],
        blank=True,
        help_text="Content of the slide",
    )
    background_caption = RichTextField(blank=True, help_text="Caption for the background image")
    background_caption_fr = RichTextField(blank=True, help_text="Caption for the background image (French)")

    parent_page_types = ['AnnualReportSPAPage']
    subpage_types = []

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("slide_title"),
                FieldPanel("slide_title_fr"),
                FieldPanel("slide_subtitle"),
                FieldPanel("slide_type"),
                FieldPanel("year"),
            ],
            heading="Slide title",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("ar_slide_content"),
            ],
            heading="Slide Content",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("background_image"),
                FieldPanel("background_video", widget=AdminMediaChooser),
                FieldPanel("background_colour"),
                FieldPanel("background_images"),
                FieldPanel("background_caption"),
                FieldPanel("background_caption_fr"),
            ],
            heading="Background",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("include_on_toc"),
            ],
            heading="Slide Settings",
            classname="collapsible collapsed",
        ),
    ]

    def get_annual_report_slide_content(self):
        content = {}
        if self.slide_type == 'toc':
            boards = {}
            credits_message = {"paragraphs": []}
            for block in self.ar_slide_content:
                if block.block_type == "board":
                    board_block = block.value
                    board_type = board_block["board_type"]

                    boards.setdefault(board_type, [])

                    for member in board_block["board_members"]:
                        if member.block_type == "member":
                            boards[board_type].append({
                                "name": member.value["name"],
                                "title": member.value["title"],
                                "title_fr": member.value["title_fr"],
                            })

                if block.block_type == "paragraph_column":
                    credits_message["paragraphs"].append({
                        "en": block.value.get("en") or "",
                        "fr": block.value.get("fr") or "",
                    })

            content = {
                "boards": boards,
                "credits_message": credits_message,
            }
        return content

    def serve(self, request):
        """Always serve the SPA regardless of sub-page requested."""
        parent = self.get_parent().specific
        return render(request, "annual_reports/annual_report_spa_page.html", {"page": parent, "self": self})


class StrategicPlanSPAPage(FeatureablePageAbstract, Page, ShareablePageAbstract, SearchablePageAbstract):
    """View annual report SPA page"""

    slides = StreamField(
        [("slide", SPSlideChooserBlock())],
        blank=True,
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("slides"),
            ],
            heading="Slides",
            classname="collapsible",
        ),
    ]
    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        ShareablePageAbstract.social_panel,
        SearchablePageAbstract.search_panel,
    ]

    subpage_types = ["StrategicPlanSlidePage"]

    def get_template(self, request, *args, **kwargs):
        return "strategic_plan/strategic_plan_spa_page.html"


class StrategicPlanSlidePage(SlidePageAbstract, Page):
    """Each individual slide within the strategic plan."""

    BACKGROUND_COLOURS = SlidePageAbstract.BACKGROUND_COLOURS + [
        ("strategic_plan_yellow", "Strategic Plan Yellow"),
        ("strategic_plan_grey", "Strategic Plan Grey"),
    ]
    SLIDE_TYPES = [
        ('title', 'Title Slide'),
        ('toc', 'Table of Contents'),
        ('text', 'Text Slide'),
        ('regular', 'Regular Slide'),
        ('framework', 'Framework Slide'),
        ('timeline', 'Timeline Slide'),
    ]
    ALIGNMENT_CHOICES = [
        ('left', 'Left'),
        ('right', 'Right'),
        ('full', 'Full'),
        ('top', 'Top'),
        ('none', 'None'),
    ]
    COLUMN_SIZES = [
        ('small', 'Small'),
        ('large', 'Large'),
    ]

    slide_type = models.CharField(
        max_length=255,
        choices=SLIDE_TYPES,
        default="regular",
        help_text="Type of slide",
    )
    strategic_plan_slide_content = StreamField(
        [
            ("column", RichTextBlock(features=[
                "bold", "italic", "h2", "h3", "h3", "ol", "ul", "link", "coloured"
            ])),
            ("acknowledgements", RichTextBlock()),
            ("framework_block", SPSlideFrameworkBlock()),
            ("board", SPSlideBoardBlock()),
        ],
        blank=True,
        help_text="Content of the slide",
    )
    background_colour = models.CharField(
        max_length=255,
        choices=BACKGROUND_COLOURS,
        blank=True,
        help_text="Background colour for the slide",
    )
    column_size = models.CharField(
        max_length=255,
        choices=COLUMN_SIZES,
        blank=True,
        help_text="Column size (only for regular slides)",
    )
    alignment = models.CharField(
        max_length=255,
        choices=ALIGNMENT_CHOICES,
        blank=True,
        help_text="Alignment of the columns (only for regular slides)",
    )
    display_vertical_title = models.BooleanField(
        default=True,
        help_text="Display the title vertically",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("slide_type"),
                FieldPanel("slide_title"),
                FieldPanel("slide_subtitle"),
                FieldPanel("strategic_plan_slide_content"),
            ],
            heading="Slide Content",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("background_image"),
                FieldPanel("background_video"),
                FieldPanel("background_colour"),
                FieldPanel("background_images"),
            ],
            heading="Background",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("include_on_toc"),
                FieldPanel("display_vertical_title"),
            ],
            heading="Slide Settings",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("column_size"),
                FieldPanel("alignment"),
            ],
            heading="Layout",
            classname="collapsible collapsed",
        ),
    ]

    parent_page_types = ["StrategicPlanSPAPage"]
    subpage_types = []

    def get_strategic_plan_slide_content(self):
        content = {
            'columns': [],
            'acknowledgements': [],
            'framework_blocks': [],
            'board': [],
        }

        for block in self.strategic_plan_slide_content:
            if block.block_type == 'column':
                content['columns'].append(expand_db_html(block.value.source))
            elif block.block_type == 'acknowledgements':
                content['acknowledgements'].append(expand_db_html(block.value.source))
            elif block.block_type == 'framework_block':
                block = {
                    'title': block.value['title'],
                    'subtitle': block.value['subtitle'],
                    'content': [text_block.value.source for text_block in block.value['text_stream']],
                    'colour': block.value['colour'],
                }
                content['framework_blocks'].append(block)
            elif block.block_type == 'board':
                member_block = [{
                    'title': member.value['title'],
                    'name': member.value['name'],
                } for member in block.value['board_members']]
                content['board'].append(member_block)

        if not content['columns']:
            content.pop('columns')
        if not content['acknowledgements']:
            content.pop('acknowledgements')
        if not content['framework_blocks']:
            content.pop('framework_blocks')
        if not content['board']:
            content.pop('board')
        return content

    def serve(self, request):
        """Always serve the SPA regardless of sub-page requested."""
        parent = self.get_parent().specific
        return render(request, "strategic_plan/strategic_plan_spa_page.html", {"page": parent, "self": self})
