from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
# from rest_framework.routers import DefaultRouter
from research import views as research_views
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views

# api_router = WagtailAPIRouter('wagtailapi')
#
# api_router.register_endpoint('article_series', ArticleSeriesPageViewSet)
# api_router.register_endpoint('content', ContentPageViewSet)
# api_router.register_endpoint('events', EventPageViewSet)
# api_router.register_endpoint('media_articles', MediaPageViewSet)
# api_router.register_endpoint('multimedia', MultimediaPageViewSet)
# api_router.register_endpoint('opinions', OpinionPageViewSet)
# api_router.register_endpoint('publication_types', PublicationTypePageViewSet)
# api_router.register_endpoint('publications', PublicationPageViewSet)
# api_router.register_endpoint('topics', TopicPageViewSet)

# api_router = DefaultRouter()
# api_router.register(r'search', search_views.search_api)

urlpatterns = [
    url(r'^django-admin/', admin.site.urls),

    url(r'^admin/', include(wagtailadmin_urls)),
    # url(r'^api/', include(api_router.urls)),
    url(r'^documents/', include(wagtaildocs_urls)),

    url(r'^search/$', search_views.search, name='search'),
    url(r'^api/search/$', search_views.search_api),
    url(r'^api/topics/$', research_views.all_topics),
]


if settings.DEBUG:  # pragma: no cover
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    url(r"", include(wagtail_urls)),

    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    url(r"^pages/", include(wagtail_urls)),
]
