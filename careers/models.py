from core.models import (
    BasicPageAbstract,
    FeatureablePageAbstract,
    ShareablePageAbstract,
)
from django.db import models


class JobPostingListPage(BasicPageAbstract):
    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = ['careers.JobPostingPage']
    templates = 'careers/job_posting_list_page.html'

    class Meta:
        verbose_name = 'Careers Page'


class JobPostingPage(FeatureablePageAbstract, ShareablePageAbstract):
    closing_date = models.DateField()

    parent_page_types = ['careers.JobPostingListPage']
    subpage_types = []
    templates = 'careers/job_posting_page.html'

    class Meta:
        verbose_name = 'Job Posting'
        verbose_name_plural = 'Job Postings'
