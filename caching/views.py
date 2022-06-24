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
class CachingReportFilterSet(WagtailFilterSet):
    theme = ChoiceFilter(field_name='theme', choices=Theme.objects.all().values_list('id', 'name'))
    article_series__title = ChoiceFilter(field_name='article_series__title', choices=ArticleSeriesPage.objects.all().values_list('title', 'title'))
    article_series__title

    class Meta:
        model = Page
        fields = ['theme', 'article_series__title']

# view that lists most recent article pages


class RecentArticlesView(PageReportView):
    template_name = "caching/recent_articles.html"
    title = _("Recent articles")
    header_icon = "list-ul"
    list_export = PageReportView.list_export
    filterset_class = CachingReportFilterSet

    # query set that returns all article pages
    def get_queryset(self):
        return ArticlePage.objects.live().order_by('-first_published_at')

def clear_cache(request, page_id):
    page = get_object_or_404(Page, id=page_id).specific
    keys = cache.keys(f'*Id:{page.id}*')
    cache.delete(*keys)
    messages.success(request, _("Cache cleared for page: " + page.title))

    redirect_to = request.POST.get('next', None)
    if redirect_to and url_has_allowed_host_and_scheme(url=redirect_to, allowed_hosts={request.get_host()}):
        return redirect(redirect_to)
    else:
        return redirect('/admin/caching/')