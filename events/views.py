from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.cache import never_cache

from .models import EventPage


@never_cache
def events_api(request):
    """
    List events by month and year. Defaults to current month and year.
    """
    try:
        month = int(request.GET.get('month', ''))
        year = int(request.GET.get('year', ''))
    except ValueError:
        now = timezone.now()
        month = now.month
        year = now.year

    events = []
    queryset = EventPage.objects.live().public().filter(
        add_to_calendar=True,
        publishing_date__year=year,
        publishing_date__month=month,
    ).exclude(path__startswith='00010002').exclude(exclude_from_search=True)
    for event_page in queryset:
        events.append({
            "title": event_page.title,
            "publishing_date": event_page.publishing_date.isoformat(),
            "url": event_page.get_url(request),
        })
    return JsonResponse({"meta": {"total_count": len(events)}, "items": events})
