from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.shortcuts import redirect
from django.utils import translation
from wagtail.admin.edit_handlers import (FieldPanel, MultiFieldPanel,
                                         PageChooserPanel, StreamFieldPanel)
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.blocks import PageChooserBlock
from wagtail.core.fields import StreamField
from wagtail.core.models import Orderable, Page
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailmedia.edit_handlers import MediaChooserPanel

from core.models import (BasicPageAbstract, FeatureablePageAbstract,
                         SearchablePageAbstract, ShareablePageAbstract)
from streams.blocks import (ParagraphBlock, PersonBlock,
                            SlideAcknowledgedGroupBlock, SlideLinkBlock,
                            SlideQuoteBlock, SlideTabBlock)


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
    )

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.hero_link_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
        MultiFieldPanel(
            [
                StreamFieldPanel('featured_reports'),
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
    search_fields = Page.search_fields + BasicPageAbstract.search_fields

    class Meta:
        verbose_name = 'Annual Report List Page'


class AnnualReportPage(RoutablePageMixin, FeatureablePageAbstract, Page, SearchablePageAbstract):
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
                DocumentChooserPanel('report_english'),
                DocumentChooserPanel('report_french'),
                DocumentChooserPanel('report_financial'),
                FieldPanel('report_interactive'),
            ],
            heading='Reports',
            classname='collapsible',
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel('image_poster'),
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
    subpage_types = [
        'annual_reports.SummarySlidePage',
        'annual_reports.MessageSlidePage',
        'annual_reports.ContentSlidePage',
        'annual_reports.OutputsAndActivitiesSlidePage',
        'annual_reports.TimelineSlidePage',
        'annual_reports.TabbedSlidePage',
    ]
    templates = 'annual_reports/annual_report_page.html'

    class Meta:
        verbose_name = 'Annual Report Page'
        verbose_name_plural = 'Annual Report Pages'

    def as_json(self):
        localized_reports = dict()
        for language_code, _ in settings.WAGTAIL_CONTENT_LANGUAGES:
            with translation.override(language_code):
                annual_report = self.localized
                base_url = self.get_url(current_site=self.get_site())
                interactive_url = base_url + annual_report.reverse_subpage("interactives", args=(language_code, ))
                localized_reports[language_code] = {
                    "title": annual_report.title,
                    "slug": annual_report.slug,
                    "url": interactive_url,
                    "locale": language_code,
                    "year": annual_report.year,
                    "slides": [
                        slide.as_json()
                        for slide in annual_report.get_children().specific()
                    ],
                }

        return {
            "id": self.id,
            "type": self._meta.model_name,
            "value": localized_reports
        }

    @route(r'^interactives/$')
    def interactives_index(self, request):
        url = self.get_url(current_site=self.get_site()) + self.reverse_subpage('interactives', args=('en', ))
        return redirect(url)

    @route(r'^interactives/(?P<locale>[\w-]+)/$')
    @route(r'^interactives/(?P<locale>[\w-]+)/(?P<slug>[\w-]+)/$')
    def interactives(self, request, locale, slug=None):
        with translation.override(locale):
            page = self.localized
        return self.render(
            request,
            template='annual_reports/annual_report_interactives.html',
            context_overrides={'annual_report_json': page.as_json(), 'self': page}
        )


class BaseSlidePage(Orderable, ShareablePageAbstract, Page):
    background_image = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Background image',
    )
    background_video = models.ForeignKey(
        'wagtailmedia.Media',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Background video',
    )
    quote = StreamField([('quote', SlideQuoteBlock())], min_num=0, max_num=1, blank=True)

    background_panel = MultiFieldPanel(
        [
            ImageChooserPanel('background_image'),
            MediaChooserPanel('background_video'),
            FieldPanel('quote'),
        ],
        heading='Background',
    )
    content_panels = Page.content_panels + [background_panel]
    promote_panels = Page.promote_panels + [ShareablePageAbstract.social_panel]
    parent_page_types = ['annual_reports.AnnualReportPage']
    subpage_types = []

    class Meta:
        abstract = True

    def as_json(self):
        return {
            "id": self.id,
            "translation_key": self.translation_key,
            "type": self._meta.model_name,
            "value": {
                "title": self.title,
                "slug": self.slug,
                "url": self.get_url(current_site=self.get_site()),
                "locale": self.locale.language_code,
                "background_image": self.background_image_dict,
                "background_video": self.background_video_dict,
                "quote": self.quote_dict,
            },
        }

    @property
    def quote_dict(self):
        quote = None
        if len(self.quote):
            first_quote = self.quote[0]
            quote = first_quote.block.get_api_representation(first_quote.value)
        return quote

    @property
    def background_image_dict(self):
        if self.background_image is None:
            return
        return {
            "original": self.background_image.get_rendition("original").file.url,
            "thumbnail": self.background_image.get_rendition("width-100").file.url,
        }

    @property
    def background_video_dict(self):
        if self.background_video is None:
            return
        return {
            "original": self.background_video.url,
            "thumbnail": self.background_video.thumbnail.url if self.background_video.thumbnail else None,
        }

    def get_template(self, request, *args, **kwargs):
        return 'annual_reports/annual_report_interactives.html'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['annual_report_json'] = self.get_parent().specific.as_json()
        return context

    def set_url_path(self, parent):
        """Localized URL path for each slide"""
        if parent:
            self.url_path = parent.url_path + 'interactives/' + self.locale.language_code + '/' + self.slug + '/'
        else:
            # a page without a parent is the tree root, which always has a url_path of '/'
            self.url_path = '/'

        return self.url_path


class SummarySlidePage(BaseSlidePage):
    max_count_per_parent = 1
    acknowledgement_message = StreamField([
        ('paragraph', ParagraphBlock()),
    ])
    acknowledged_groups = StreamField([('acknowledged_group', SlideAcknowledgedGroupBlock())])

    content_panels = BaseSlidePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('acknowledgement_message'),
                FieldPanel('acknowledged_groups'),
            ],
            heading='Acknowledgements',
        ),
    ]
    template = 'annual_reports/annual_report_interactives.html'

    def as_json(self):
        acknowledgement = {
            "message": self.acknowledgement_message.stream_block.get_api_representation(self.acknowledgement_message),
            "groups": self.acknowledged_groups.stream_block.get_api_representation(self.acknowledged_groups)
        }

        json_response = super().as_json()
        json_response["value"]["acknowledgement"] = acknowledgement
        return json_response


class MessageSlidePage(BaseSlidePage):
    body = StreamField([('paragraph', ParagraphBlock())])
    author = models.ForeignKey(
        'people.PersonPage',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='message_slides_as_author',
        verbose_name='Author',
    )

    content_panels = BaseSlidePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('body'),
                PageChooserPanel('author', ['people.PersonPage']),
            ],
            heading='Message',
        ),
    ]

    def as_json(self):
        data = {
            "body": self.body.stream_block.get_api_representation(self.body),
            "author": PersonBlock('people.Person').get_api_representation(self.author),
        }
        json_response = super().as_json()
        json_response['value'].update(data)
        return json_response


class ContentSlidePage(BaseSlidePage):
    body = StreamField([('paragraph', ParagraphBlock())])
    links = StreamField([('link', SlideLinkBlock())], blank=True)

    content_panels = BaseSlidePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('body'),
                FieldPanel('links'),
            ],
            heading='Content',
        ),
    ]

    def as_json(self):
        data = {
            "links": self.links.stream_block.get_api_representation(self.links),
            "body": self.body.stream_block.get_api_representation(self.body)
        }
        json_response = super().as_json()
        json_response['value'].update(data)
        return json_response


class OutputsAndActivitiesSlidePage(BaseSlidePage):
    max_count_per_parent = 1


class TimelineSlidePage(BaseSlidePage):
    max_count_per_parent = 1


class TabbedSlidePage(BaseSlidePage):
    tabs = StreamField([('tab', SlideTabBlock())])

    content_panels = BaseSlidePage.content_panels + [
        FieldPanel('tabs'),
    ]

    def as_json(self):
        data = {
            "tabs": self.tabs.stream_block.get_api_representation(self.tabs)
        }
        json_response = super().as_json()
        json_response['value'].update(data)
        return json_response
