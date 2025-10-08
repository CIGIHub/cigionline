from django.http import Http404
from core.models import (
    BasicPageAbstract,
    FeatureablePageAbstract,
    SearchablePageAbstract,
    ShareablePageAbstract
)
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.shortcuts import render
from django.utils.text import slugify
from streams.blocks import ARFinancialPositionBlock, ARFinancialsAuditorReportBlock, ARFundBalancesBlock, ARSlideBoardBlock, ARSlideChooserBlock, ARSlideColumnBlock, SPSlideBoardBlock, SPSlideChooserBlock, SPSlideFrameworkBlock
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
)
from wagtail.blocks import PageChooserBlock, RichTextBlock
from wagtail.fields import StreamField, RichTextField
from wagtail.models import Page
from wagtail.rich_text import expand_db_html
from django.utils.html import strip_tags
from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.models import Media
from wagtailmedia.widgets import AdminMediaChooser
from wagtail.contrib.routable_page.models import RoutablePageMixin, route


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


class AnnualReportSPAPage(RoutablePageMixin, FeatureablePageAbstract, SearchablePageAbstract, ShareablePageAbstract, Page):
    """View annual report SPA page"""

    year = models.PositiveIntegerField(blank=False, null=True)
    slides = StreamField(
        [("slide", ARSlideChooserBlock())],
        blank=True,
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("year"),
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

    @route(r'^(?P<lang>en|fr)/(?P<slide_slug>[-\w]+)/(?P<subslug>[-\w]+)/?$')
    def slide_with_lang_and_subslug(self, request, lang, slide_slug, subslug, *args, **kwargs):
        slide = (self.get_children()
                 .type(AnnualReportSlidePage)
                 .live()
                 .filter(slug=slide_slug)
                 .specific()
                 .first())
        if not slide:
            raise Http404("Slide not found")
        return slide._serve_spa(request, initial_lang=lang)


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


class AnnualReportSlidePage(RoutablePageMixin, SlidePageAbstract, Page):
    """Each individual slide within the annual report."""

    def _serve_spa(self, request, initial_lang="en"):
        parent = self.get_parent().specific
        ctx = {
            "page": parent,
            "self": self,
            "initial_lang": initial_lang,
        }
        return render(request, "annual_reports/annual_report_spa_page.html", ctx)

    @route(r"^$")
    def slide_root(self, request, *args, **kwargs):
        return self._serve_spa(request, initial_lang="en")

    @route(r"^fr/?$")
    def slide_fr(self, request, *args, **kwargs):
        return self._serve_spa(request, initial_lang="fr")

    @route(r"^(?P<trailing>[/]+)?$")
    def slide_catchall(self, request, trailing=None, *args, **kwargs):
        return self._serve_spa(request, initial_lang="en")

    SLIDE_TYPES = [
        ('title', 'Title'),
        ('toc', 'Table of Contents'),
        ('chairs_message', 'Chair\'s Message'),
        ('presidents-message', 'President\'s Message'),
        ('standard', 'Standard'),
        ('outputs_and_activities', 'Outputs and Activities'),
        ('timeline', 'Timeline'),
        ('financials', 'Financials'),
    ]

    QUOTE_POSITIONS = [
        ('right', 'Right'),
        ('left', 'Left'),
        ('top-left', 'Top Left'),
        ('top-right', 'Top Right'),
        ('bottom-left', 'Bottom Left'),
        ('bottom-right', 'Bottom Right'),
    ]

    slide_type = models.CharField(
        max_length=255,
        choices=SLIDE_TYPES,
        default='standard',
        help_text='Type of slide',
    )

    slide_title_fr = models.CharField(max_length=255, help_text="Title of the slide (French)", blank=True)

    ar_slide_content = StreamField(
        [
            ("column", ARSlideColumnBlock()),
            ("board", ARSlideBoardBlock()),
            ("auditor_report", ARFinancialsAuditorReportBlock()),
            ("financial_position", ARFinancialPositionBlock()),
            ("fund_balances", ARFundBalancesBlock()),
        ],
        blank=True,
        help_text="Content of the slide",
    )
    download_pdf = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    background_quote = RichTextField(blank=True, help_text="quote for the background image", features=['bold', 'italic', 'link', 'source'])
    background_quote_fr = RichTextField(blank=True, help_text="quote for the background image (French)", features=['bold', 'italic', 'link', 'source'])
    background_quote_position = models.CharField(
        max_length=255,
        choices=QUOTE_POSITIONS,
        blank=True,
        help_text="Position of the quote",
    )

    parent_page_types = ['AnnualReportSPAPage']
    subpage_types = []

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("slide_title"),
                FieldPanel("slide_title_fr"),
                FieldPanel("slide_subtitle"),
                FieldPanel("slide_type"),
            ],
            heading="Slide title",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("ar_slide_content"),
                FieldPanel("download_pdf"),
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
                FieldPanel("background_quote"),
                FieldPanel("background_quote_fr"),
                FieldPanel("background_quote_position"),
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
            credits_message = {}
            member_counter = 1

            for block in self.ar_slide_content:
                if block.block_type == "board":
                    board_block = block.value
                    board_type = board_block["board_type"]

                    boards.setdefault(board_type, [])

                    for member in board_block["board_members"]:
                        if member.block_type == "member":
                            image = member.value.get("image_override") or (member.value.get("page").specific.image_square if member.value.get("page") else None)
                            link = member.value.get("link_override") or (member.value.get("page").specific.url if member.value.get("page") else None)
                            boards[board_type].append({
                                "id": member_counter,
                                "name": member.value["name"],
                                "title": member.value["title"],
                                "title_fr": member.value["title_fr"],
                                "title_line_2": member.value.get("title_line_2", ""),
                                "title_line_2_fr": member.value.get("title_line_2_fr", ""),
                                "bio_en": expand_db_html(member.value.get("bio_en").source) if member.value.get("bio_en") else "",
                                "bio_fr": expand_db_html(member.value.get("bio_fr").source) if member.value.get("bio_fr") else "",
                                "image": image.get_rendition('fill-150x150').file.url if image else '',
                                "link": link,
                            })
                            member_counter += 1

                if block.block_type == "column":
                    column = block.value.get("column")
                    for paragraph_column in column:
                        if paragraph_column.block_type == "paragraph_column":
                            credits_message["en"] = strip_tags(paragraph_column.value.get("en").source) or ""
                            credits_message["fr"] = strip_tags(paragraph_column.value.get("fr").source) or ""

            content = {
                "boards": boards,
                "credits_message": credits_message,
            }

        elif self.slide_type in ['chairs_message', 'presidents_message']:
            columns = []
            for block in self.ar_slide_content:
                if block.block_type == "column":
                    column = block.value.get("column")
                    column_content = {
                        "en": [],
                        "fr": [],
                    }
                    for paragraph_column in column:
                        if paragraph_column.block_type == "paragraph_column":
                            column_content["en"].append(expand_db_html(paragraph_column.value.get("en").source))
                            column_content["fr"].append(expand_db_html(paragraph_column.value.get("fr").source))
                    columns.append(column_content)
            content = {
                "columns": columns,
            }
        elif self.slide_type == 'standard':
            columns = []
            for block in self.ar_slide_content:
                if block.block_type == "column":
                    column = block.value.get("column")
                    column_content = {
                        "en": [],
                        "fr": [],
                        "content": [],
                    }
                    for subblock in column:
                        if subblock.block_type == "paragraph_column":
                            column_content["en"].append(
                                expand_db_html(subblock.value.get("en").source)
                            )
                            column_content["fr"].append(
                                expand_db_html(subblock.value.get("fr").source)
                            )

                        elif subblock.block_type == "content_column":
                            for content_item in subblock.value:
                                if content_item.block_type == "content":
                                    content_val = content_item.value
                                    link = content_val.get("link_override") or (content_val.get("page").specific.url if content_val.get("page") else None)
                                    column_content["content"].append({
                                        "type": content_val.get("type"),
                                        "link": link,
                                        "title_en": content_val.get("title_en"),
                                        "title_fr": content_val.get("title_fr"),
                                    })

                    columns.append(column_content)

            content = {
                "columns": columns,
            }
        elif self.slide_type == 'financials':
            auditor_reports = []
            financial_position = []
            tabs = []
            pdf = self.download_pdf.file.url if self.download_pdf else ''
            for block in self.ar_slide_content:
                if block.block_type == "auditor_report":
                    columns = []
                    for column_block in (block.value.get("columns") or []):
                        en_stream = column_block.value.get("en") or []
                        fr_stream = column_block.value.get("fr") or []

                        col = {"en": [], "fr": []}

                        for child in en_stream:
                            if child.block_type == "paragraph":
                                rt = child.value
                                col["en"].append(expand_db_html(rt.source))
                            elif child.block_type == "signature":
                                sig = child.value
                                sig_img = sig.get("signature")
                                col["en"].append({
                                    "signature": (sig_img.get_rendition('fill-105x18').file.url if sig_img else ''),
                                    "signature_text": expand_db_html(sig.get("signature_text").source) if sig.get("signature_text") else "",
                                })
                            else:
                                # future-proof: pass through unknown child types as strings
                                col["en"].append(str(child.value))

                        # FR stream items
                        for child in fr_stream:
                            if child.block_type == "paragraph":
                                rt = child.value
                                col["fr"].append(expand_db_html(rt.source))
                            elif child.block_type == "signature":
                                sig = child.value
                                sig_img = sig.get("signature")
                                col["fr"].append({
                                    "signature": (sig_img.get_rendition('fill-105x18').file.url if sig_img else ''),
                                    "signature_text": expand_db_html(sig.get("signature_text").source) if sig.get("signature_text") else "",
                                })
                            else:
                                col["fr"].append(str(child.value))

                        columns.append(col)

                    title_en = block.value.get("title_en") or ""
                    title_fr = block.value.get("title_fr") or ""

                    auditor_reports = {
                        "title_en": title_en,
                        "title_fr": title_fr,
                        "slug_en": slugify(title_en) if title_en else "auditor-report-en",
                        "slug_fr": slugify(title_fr) if title_fr else "auditor-report-fr",
                        "columns": columns,
                    }

                    tabs.append(auditor_reports)
                elif block.block_type == "financial_position":
                    title_en = block.value.get("title_en") or ""
                    title_fr = block.value.get("title_fr") or ""
                    description_en = expand_db_html(block.value.get("description_en").source) or ""
                    description_fr = expand_db_html(block.value.get("description_fr").source) or ""
                    amounts = block.value.get("amounts")
                    current_year = amounts.get("year_current")
                    previous_year = amounts.get("year_previous")
                    year_current = {
                        "year_label": current_year.get("year_label"),
                        "cash_and_cash_equivalents": current_year.get("cash_and_cash_equivalents") or "",
                        "portfolio_investments": current_year.get("portfolio_investments") or "",
                        "amounts_receivable": current_year.get("amounts_receivable") or "",
                        "prepaid_expenses": current_year.get("prepaid_expenses") or "",
                        "current_assets_subtotal": current_year.get("current_assets_subtotal") or "",
                        "property_and_equipment": current_year.get("property_and_equipment") or "",
                        "lease_inducement": current_year.get("lease_inducement") or "",
                        "other_assets_subtotal": current_year.get("other_assets_subtotal") or "",
                        "total_assets": current_year.get("total_assets") or "",
                        "accounts_payable_and_accrued_liabilities": current_year.get("accounts_payable_and_accrued_liabilities") or "",
                        "deferred_revenue": current_year.get("deferred_revenue") or "",
                        "total_liabilities": current_year.get("total_liabilities") or "",
                        "invested_in_capital_assets": current_year.get("invested_in_capital_assets") or "",
                        "externally_restricted": current_year.get("externally_restricted") or "",
                        "internally_restricted": current_year.get("internally_restricted") or "",
                        "unrestricted": current_year.get("unrestricted") or "",
                        "total_fund_balances": current_year.get("total_fund_balances") or "",
                        "total_liabilities_and_fund_balances": current_year.get("total_liabilities_and_fund_balances") or "",
                    }
                    year_previous = {
                        "year_label": previous_year.get("year_label"),
                        "cash_and_cash_equivalents": previous_year.get("cash_and_cash_equivalents") or "",
                        "portfolio_investments": previous_year.get("portfolio_investments") or "",
                        "amounts_receivable": previous_year.get("amounts_receivable") or "",
                        "prepaid_expenses": previous_year.get("prepaid_expenses") or "",
                        "current_assets_subtotal": previous_year.get("current_assets_subtotal") or "",
                        "property_and_equipment": previous_year.get("property_and_equipment") or "",
                        "lease_inducement": previous_year.get("lease_inducement") or "",
                        "other_assets_subtotal": previous_year.get("other_assets_subtotal") or "",
                        "total_assets": previous_year.get("total_assets") or "",
                        "accounts_payable_and_accrued_liabilities": previous_year.get("accounts_payable_and_accrued_liabilities") or "",
                        "deferred_revenue": previous_year.get("deferred_revenue") or "",
                        "total_liabilities": previous_year.get("total_liabilities") or "",
                        "invested_in_capital_assets": previous_year.get("invested_in_capital_assets") or "",
                        "externally_restricted": previous_year.get("externally_restricted") or "",
                        "internally_restricted": previous_year.get("internally_restricted") or "",
                        "unrestricted": previous_year.get("unrestricted") or "",
                        "total_fund_balances": previous_year.get("total_fund_balances") or "",
                        "total_liabilities_and_fund_balances": previous_year.get("total_liabilities_and_fund_balances") or "",
                    }
                    financial_position = {
                        "title_en": title_en,
                        "title_fr": title_fr,
                        "description_en": description_en,
                        "description_fr": description_fr,
                        "slug_en": slugify(title_en) if title_en else "financial-position-en",
                        "slug_fr": slugify(title_fr) if title_fr else "financial-position-fr",
                        "year_current": year_current,
                        "year_previous": year_previous,
                    }
                    tabs.append(financial_position)
                elif block.block_type == "fund_balances":
                    title_en = block.value.get("title_en") or ""
                    title_fr = block.value.get("title_fr") or ""
                    description_en = expand_db_html(block.value.get("description_en").source) or ""
                    description_fr = expand_db_html(block.value.get("description_fr").source) or ""
                    amounts = block.value.get("amounts")
                    current_year = amounts.get("year_current")
                    previous_year = amounts.get("year_previous")
                    year_current = {
                        "year_label": current_year.get("year_label"),
                        "realized_investment_income": current_year.get("realized_investment_income") or "",
                        "unrealized_investment_gains": current_year.get("unrealized_investment_gains") or "",
                        "other": current_year.get("other") or "",
                        "government_and_other_grants": current_year.get("government_and_other_grants") or "",
                        "total_revenue": current_year.get("total_revenue") or "",
                        "research_and_conferences": current_year.get("research_and_conferences") or "",
                        "amortization": current_year.get("amortization") or "",
                        "administration": current_year.get("administration") or "",
                        "facilities": current_year.get("facilities") or "",
                        "technical_support": current_year.get("technical_support") or "",
                        "total_expenses": current_year.get("total_expenses") or "",
                        "excess_of_expenses_over_revenue": current_year.get("excess_of_expenses_over_revenue") or "",
                        "fund_balances_beginning_of_year": current_year.get("fund_balances_beginning_of_year") or "",
                        "fund_balances_end_of_year": current_year.get("fund_balances_end_of_year") or "",
                    }
                    year_previous = {
                        "year_label": previous_year.get("year_label"),
                        "realized_investment_income": previous_year.get("realized_investment_income") or "",
                        "unrealized_investment_gains": previous_year.get("unrealized_investment_gains") or "",
                        "other": previous_year.get("other") or "",
                        "government_and_other_grants": previous_year.get("government_and_other_grants") or "",
                        "total_revenue": previous_year.get("total_revenue") or "",
                        "research_and_conferences": previous_year.get("research_and_conferences") or "",
                        "amortization": previous_year.get("amortization") or "",
                        "administration": previous_year.get("administration") or "",
                        "facilities": previous_year.get("facilities") or "",
                        "technical_support": previous_year.get("technical_support") or "",
                        "total_expenses": previous_year.get("total_expenses") or "",
                        "excess_of_expenses_over_revenue": previous_year.get("excess_of_expenses_over_revenue") or "",
                        "fund_balances_beginning_of_year": previous_year.get("fund_balances_beginning_of_year") or "",
                        "fund_balances_end_of_year": previous_year.get("fund_balances_end_of_year") or "",
                    }
                    fund_balances = {
                        "title_en": title_en,
                        "title_fr": title_fr,
                        "description_en": description_en,
                        "description_fr": description_fr,
                        "slug_en": slugify(title_en) if title_en else "fund-balances-en",
                        "slug_fr": slugify(title_fr) if title_fr else "fund-balances-fr",
                        "year_current": year_current,
                        "year_previous": year_previous,
                    }
                    tabs.append(fund_balances)

            content = {
                "tabs": tabs,
                "pdf": pdf,
            }
        return content


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
