from email import message
from tkinter import Widget
from django_filters import ChoiceFilter
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.utils.http import url_has_allowed_host_and_scheme
from wagtail.admin import messages
from wagtail.admin.filters import WagtailFilterSet
from wagtail.admin.views.reports.base import PageReportView
from wagtail.core.models import Page
from articles.models import ArticlePage, ArticleSeriesPage
from core.models import Theme


# report filter set that filters based on theme and content series fields
class CachingArticlesFilterSet(WagtailFilterSet):
    theme = ChoiceFilter(field_name='theme', choices=Theme.objects.all().values_list('id', 'name'))
    article_series__title = ChoiceFilter(field_name='article_series__title', choices=ArticleSeriesPage.objects.all().values_list('title', 'title'))
    article_series__title

    class Meta:
        model = Page
        fields = ['theme', 'article_series__title']


class CachingArticleSeriesFilterSet(WagtailFilterSet):
    theme = ChoiceFilter(field_name='theme', choices=Theme.objects.all().values_list('id', 'name'))

    class Meta:
        model = Page
        fields = ['theme']

# view that lists most recent article pages


class ArticlesView(PageReportView):
    template_name = "caching/articles.html"
    title = _("Articles")
    header_icon = "list-ul"
    list_export = PageReportView.list_export
    filterset_class = CachingArticlesFilterSet

    # query set that returns all article pages
    def get_queryset(self):
        return ArticlePage.objects.live().order_by('-first_published_at')


class ArticleSeriesView(PageReportView):
    template_name = "caching/article_series.html"
    title = _("Article Series")
    header_icon = "list-ul"
    list_export = PageReportView.list_export
    filterset_class = CachingArticleSeriesFilterSet

    # query set that returns all article pages
    def get_queryset(self):
        return ArticleSeriesPage.objects.live().order_by('-first_published_at')


def clear_article_cache(request, page_id):
    page = get_object_or_404(Page, id=page_id).specific
    keys = cache.keys(f'*Id:{page.id}*')
    cache.delete(*keys)
    messages.success(request, _("Cache cleared for page: " + page.title))

    redirect_to = request.POST.get('next', None)
    if redirect_to and url_has_allowed_host_and_scheme(url=redirect_to, allowed_hosts={request.get_host()}):
        return redirect(redirect_to)
    else:
        return redirect('/admin/caching/')


def clear_article_series_cache(request, page_id):
    series_page = get_object_or_404(Page, id=page_id).specific
    series_items = series_page.specific.series_items.all()

    keys = [cache.keys(f'*Id:{series_item.content_page.id}*') for series_item in series_items]
    keys.append(cache.keys(f'*Id{series_page.id}'))
    for key in keys:
        cache.delete(*key)

    redirect_to = request.POST.get('next', None)
    if redirect_to and url_has_allowed_host_and_scheme(url=redirect_to, allowed_hosts={request.get_host()}):
        return redirect(redirect_to)
    else:
        return redirect('/admin/caching/')
