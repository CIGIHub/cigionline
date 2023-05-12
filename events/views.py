from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.cache import cache_page

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
    queryset = EventPage.objects.live().public().filter(publishing_date__year=year, publishing_date__month=month)
    for event_page in queryset:
        events.append({
            "title": event_page.title,
            "publishing_date": event_page.publishing_date.isoformat(),
            "url": event_page.get_url(request),
        })
    return JsonResponse({"meta": {"total_count": len(events)}, "items": events})

@cache_page(60 * 60 * 24)
def all_events(request):
    event_pages = EventPage.objects.live().specific().prefetch_related(
        'authors__author', 'topics'
    ).order_by('-publishing_date')

    events_list = []
    for item in event_pages:
        item_dict = {}

        item_dict['title'] = item.feature_title if item.feature_title else item.title
        item_dict['authors'] = [{
            'title': author.author.title,
            'url': author.author.url
        } for author in item.authors.all()]
        item_dict['event_type'] = item.get_event_type_display()
        item_dict['event_access'] = item.get_event_access_display()
        item_dict['event_format'] = item.event_format_string
        item_dict['is_past'] = item.is_past()
        item_dict['time_zone_label'] = item.time_zone_label
        item_dict['url'] = item.feature_url if item.feature_url else item.url
        item_dict['topics'] = [{
            'title': topic.title,
            'url': topic.url
        } for topic in item.topics_sorted]
        item_dict['registration_url'] = item.registration_url
        item_dict['id'] = item.id
        item_dict['start_time'] = item.publishing_date.strftime('%Y-%m-%dT%H:%M:%S%z')
        item_dict['end_time'] = item.event_end.strftime('%Y-%m-%dT%H:%M:%S%z') if item.event_end else ''
        item_dict['start_utc_ts'] = item.event_start_time_utc_ts
        item_dict['end_utc_ts'] = item.event_end_time_utc_ts if item.event_end else ''

        events_list.append(item_dict)

    def batched(lst, batch_size):
        return [lst[i: i + batch_size] for i in range(0, len(lst), batch_size)]

    batched_list = batched(events_list, 4)
    events_dict = {}
    for batch in range(len(batched_list)):
        events_dict[str(batch)] = list(batched_list[batch])

    return JsonResponse({
        'meta': {
            'total_events_count': len(events_list),
            'total_page_count': len(batched_list)},
        'items': events_dict,
    })
