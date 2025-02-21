from core.models import (
    BasicPageAbstract,
    FeatureablePageAbstract,
    SearchablePageAbstract,
)
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.shortcuts import render
from streams.blocks import SlideChooserBlock
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
)
from wagtail.api import APIField
from wagtail.blocks import PageChooserBlock
from wagtail.fields import StreamField, RichTextField
from wagtail.models import Page
from wagtailmedia.models import Media


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


class AnnualReportSPAPage(FeatureablePageAbstract, Page, SearchablePageAbstract):
    """View annual report SPA page"""

    slides = StreamField(
        [("slide", SlideChooserBlock())],
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

    subpage_types = ["AnnualReportSlidePage"]


class AnnualReportSlidePage(Page):
    """Each individual slide within the annual report."""

    SLIDE_TYPES = [
        ("regular", "Regular Slide"),
        ("toc", "Table of Contents"),
    ]
    BACKGROUND_COLOURS = [
        ("white", "White"),
        ("black", "Black"),
        ("strategic_plan_yellow", "Strategic Plan Yellow"),
    ]

    slide_title = models.CharField(max_length=255, help_text="Title of the slide")
    slide_content = RichTextField(blank=True, help_text="Content of the slide")
    slide_type = models.CharField(
        max_length=255,
        choices=SLIDE_TYPES,
        default="regular",
        help_text="Type of slide",
    )
    background_image = models.ForeignKey(
        "images.CigionlineImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Background image for the slide",
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

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("slide_type"),
                FieldPanel("slide_title"),
                FieldPanel("slide_content"),
            ],
            heading="Slide Content",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("background_image"),
                FieldPanel("background_video"),
                FieldPanel("background_colour"),
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

    parent_page_types = ["AnnualReportSPAPage"]
    subpage_types = []

    def serve(self, request):
        """Always serve the SPA regardless of sub-page requested."""
        parent = self.get_parent().specific
        return render(request, "annual_reports/annual_report_spa_page.html", {"page": parent})
