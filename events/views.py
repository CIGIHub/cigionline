from django.utils import timezone
from django.http import JsonResponse

from .models import EventPage


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
    queryset = EventPage.objects.live().filter(publishing_date__year=year, publishing_date__month=month)
    for event_page in queryset:
        events.append({
            "id": event_page.id,
            "title": event_page.title,
            "publishing_date": event_page.publishing_date.isoformat(),
            "url": event_page.get_url(request),
        })
    return JsonResponse({"meta": {"total_count": len(events)}, "items": events})

