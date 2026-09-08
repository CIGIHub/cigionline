import re

from django.utils.text import slugify
from django_ical.views import ICalFeed
from events.models import EventPage


class EventFeed(ICalFeed):
    def __call__(self, request, *args, **kwargs):
        self.request = request
        return super(EventFeed, self).__call__(request, *args, **kwargs)

    def file_name(self):
        event = self.items().first()
        if event:
            return f'{slugify(event.title) or "event"}.ics'
        return 'event.ics'

    def items(self):
        try:
            event_id = int(self.request.GET.get('id'))
        except (TypeError, ValueError):
            return EventPage.objects.none()
        return EventPage.objects.live().public().filter(id=event_id)

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return re.sub('<[^<]+?>', '', item.subtitle or '')

    def item_start_datetime(self, item):
        return item.event_start_time_utc

    def item_end_datetime(self, item):
        return item.calendar_end_time_utc

    def item_link(self, item):
        return item.full_url or item.url

    def item_location(self, item):
        return item.location_string()
