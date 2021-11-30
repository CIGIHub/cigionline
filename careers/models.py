from core.models import (
    BasicPageAbstract,
    FeatureablePageAbstract,
    SearchablePageAbstract,
    ShareablePageAbstract,
)
from django.db import models
from django.template.defaultfilters import date
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.documents.blocks import DocumentChooserBlock


class JobPostingListPage(BasicPageAbstract, Page):
    def get_context(self, request):
        context = super().get_context(request)
        context['job_postings'] = JobPostingPage.objects.live().public().order_by(models.F('closing_date').asc(nulls_first=True))
        return context

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = ['careers.JobPostingPage', 'core.BasicPage']
    templates = 'careers/job_posting_list_page.html'

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields

    class Meta:
        verbose_name = 'Careers Page'


class JobPostingPage(
    FeatureablePageAbstract,
    Page,
    SearchablePageAbstract,
    ShareablePageAbstract,
):
    closing_date = models.DateField(blank=True, null=True)
    description = StreamField(
        BasicPageAbstract.body_default_blocks,
        blank=True,
    )
    related_files = StreamField(
        [
            ('file', DocumentChooserBlock()),
        ],
        blank=True,
    )
    short_description = RichTextField(
        blank=True,
        null=False,
        features=['bold', 'italic', 'link'],
    )

    @property
    def closing_date_text(self):
        if self.closing_date:
            return 'Closing Date: %s' % date(self.closing_date, 'l F j, Y')
        return ''

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel('title'),
                FieldPanel('short_description'),
            ],
            heading='Title',
            classname='collapsible',
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('description'),
            ],
            heading='Job Description',
            classname='collapsible',
        ),
        MultiFieldPanel(
            [
                FieldPanel('closing_date'),
            ],
            heading='Closing Date',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('related_files'),
            ],
            heading='Related Files',
            classname='collapsible collapsed',
        ),
    ]
    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        ShareablePageAbstract.social_panel,
        SearchablePageAbstract.search_panel,
    ]

    search_fields = Page.search_fields + SearchablePageAbstract.search_fields

    parent_page_types = ['careers.JobPostingListPage']
    subpage_types = []
    templates = 'careers/job_posting_page.html'

    class Meta:
        verbose_name = 'Job Posting'
        verbose_name_plural = 'Job Postings'
