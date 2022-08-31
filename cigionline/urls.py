from annual_reports import views as annual_report_views
from django.conf import settings
from django.conf.urls import include
from django.urls import path, re_path
from django.views.decorators.cache import cache_control
from articles import views as article_views
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
        re_path(r'^admin/', include(wagtailadmin_urls)),
    ]
urlpatterns = urlpatterns + [
    re_path(r'^documents/', include(wagtaildocs_urls)),

    re_path(r'^search/$', search_views.search, name='search'),
    re_path(r'^api/experts/$', people_views.all_experts),
    re_path(r'^api/all_experts_search/$', people_views.all_experts_search),
    re_path(r'^api/search/$', search_views.search_api),
    re_path(r'^api/staff/$', people_views.all_staff),
    re_path(r'^api/topics/$', research_views.all_topics),
    re_path(r'^api/annual-reports/', annual_report_views.all_annual_reports),
    re_path(r'^api/events/$', events_views.events_api),
    re_path(r'^api/ar_timeline_pages/$', core_views.ar_timeline_pages),
    re_path(r'^api/old_images/$', core_views.old_images),

    re_path(r'^events/feed.ics$', EventFeed()),
    re_path(r'^favicon\.ico$', favicon_view),
    re_path(r'^robots\.txt$', robots_views.RobotsView.as_view(), name='robots'),
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
    re_path(r"", include(wagtail_urls)),

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
