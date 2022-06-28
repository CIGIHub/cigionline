from django.urls import path, include

from .views import ArticlesView, ArticleSeriesView, clear_article_cache, clear_article_series_cache

app_name = 'caching'

caching_patterns = ([
    path("articles/", ArticlesView.as_view(), name="caching_articles"),
    path("article_series/", ArticleSeriesView.as_view(), name="caching_article_series"),
    path("articles/<int:page_id>/clear_article_cache/", clear_article_cache, name="clear_article_cache"),
    path("article_series/<int:page_id>/clear_article_series_cache/", clear_article_series_cache, name="clear_article_series_cache"),
], app_name)

urlpatterns = [
    path("caching/", include(caching_patterns)),
]
