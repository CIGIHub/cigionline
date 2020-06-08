from core.models import (
    BasicPageAbstract,
    FeatureablePageAbstract,
    ShareablePageAbstract,
)
from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core.fields import RichTextField, StreamField
from wagtail.documents.blocks import DocumentChooserBlock


class JobPostingListPage(BasicPageAbstract):
    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = ['careers.JobPostingPage']
    templates = 'careers/job_posting_list_page.html'

    class Meta:
        verbose_name = 'Careers Page'


class JobPostingPage(
    FeatureablePageAbstract,
    ShareablePageAbstract,
):
    closing_date = models.DateField(blank=True, null=True)
    description = StreamField(
        BasicPageAbstract.body_streamfield_blocks,
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
        features=['bold', 'italic'],
    )

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel('title'),
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

    parent_page_types = ['careers.JobPostingListPage']
    subpage_types = []
    templates = 'careers/job_posting_page.html'

    class Meta:
        verbose_name = 'Job Posting'
        verbose_name_plural = 'Job Postings'
