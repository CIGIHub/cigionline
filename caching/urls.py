from django.urls import path, include

from .views import RecentArticlesView, clear_cache

app_name = 'caching'

caching_patterns = ([
    path("", RecentArticlesView.as_view(), name="caching_recent_articles"),
    path("<int:page_id>/clear_cache/", clear_cache, name='clear_cache'),
], app_name)

urlpatterns = [
    path("caching/", include(caching_patterns)),
]