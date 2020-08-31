from wagtail.core.models import Page


class ArticleListPage(Page):
    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = []
    templates = 'articles/article_list_page.html'

    class Meta:
        verbose_name = 'Article List Page'
