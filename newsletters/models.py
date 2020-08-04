from core.models import (
    BasicPageAbstract,
)


class NewsletterListPage(BasicPageAbstract):
    max_count = 1
    parent_page_types = ['core.Homepage']
    subpage_types = []
    templates = 'newsletter/newsletter_list_page.html'

    class Meta:
        verbose_name = 'Newsletter List Page'
