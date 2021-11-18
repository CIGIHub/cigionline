from annual_reports import views as annual_report_views
from django.conf import settings
from django.conf.urls import include, url
from django.urls import path
from django.views.decorators.cache import cache_control
from core import views as core_views
from events.feeds import EventFeed
from images.views import favicon_view
from people import views as people_views
from research import views as research_views
from robots import views as robots_views
from search import views as search_views
from events import views as events_views
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.utils.urlpatterns import decorate_urlpatterns


urlpatterns = []
if settings.ADMIN_ENABLED:
    urlpatterns = urlpatterns + [
        url(r'^admin/', include(wagtailadmin_urls)),
    ]
urlpatterns = urlpatterns + [
    url(r'^documents/', include(wagtaildocs_urls)),

    url(r'^search/$', search_views.search, name='search'),
    url(r'^api/experts/$', people_views.all_experts),
    url(r'^api/all_experts_search/$', people_views.all_experts_search),
    url(r'^api/search/$', search_views.search_api),
    url(r'^api/staff/$', people_views.all_staff),
    url(r'^api/topics/$', research_views.all_topics),
    url(r'^api/annual-reports/', annual_report_views.all_annual_reports),
    url(r'^api/events/$', events_views.events_api),
    url(r'^api/ar_timeline_pages/$', core_views.ar_timeline_pages),
    url(r'^api/metric_pages/$', core_views.metric_pages),
    url(r'^events/feed.ics$', EventFeed()),
    url(r'^favicon\.ico$', favicon_view),
    url(r'^robots\.txt$', robots_views.RobotsView.as_view(), name='robots'),
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

cache_max_age = getattr(settings, 'CACHE_CONTROL_MAX_AGE', None)
if cache_max_age:
    urlpatterns = decorate_urlpatterns(
        urlpatterns,
        cache_control(max_age=cache_max_age)
    )
