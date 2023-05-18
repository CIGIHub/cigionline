from core.models import (
    BasicPageAbstract,
    FeatureablePageAbstract,
    SearchablePageAbstract,
)
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
)
from wagtail.models import Page


class AnnualReportListPage(BasicPageAbstract, Page, SearchablePageAbstract):
    max_count = 1
    parent_page_types = ['core.BasicPage']
    subpage_types = ['annual_reports.AnnualReportPage']
    templates = 'annual_reports/annual_report_list_page.html'

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.hero_link_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
    ]
    promote_panels = Page.promote_panels + [
        SearchablePageAbstract.search_panel
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]
    search_fields = Page.search_fields + BasicPageAbstract.search_fields + SearchablePageAbstract.search_fields

    def annual_reports_list(self):
        return AnnualReportPage.objects.live().order_by('-year')

    def annual_reports_list_swiper(self):
        reports = AnnualReportPage.objects.live().order_by('-year')[1:]
        return [[reports[i], reports[i + 1]] for i in range(0, len(reports), 2)]

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
    report_interactive_fr = models.CharField(
        blank=True,
        max_length=255,
        help_text='Internal path to the FR version of the interactive report. Example: /interactives/2019annualreport/fr',
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
                FieldPanel('report_interactive_fr'),
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
    subpage_types = []
    templates = 'annual_reports/annual_report_page.html'

    class Meta:
        verbose_name = 'Annual Report Page'
        verbose_name_plural = 'Annual Report Pages'
