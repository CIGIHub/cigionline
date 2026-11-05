from django_ical.views import ICalFeed
from events.models import EventPage
import re


class EventFeed(ICalFeed):
    def __call__(self, request, *args, **kwargs):
        self.request = request
        return super(EventFeed, self).__call__(request, *args, **kwargs)

    file_name = 'calendar.ics'

    def items(self):
        return EventPage.objects.filter(id=self.request.GET.get('id'))

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return re.sub('<[^<]+?>', '', item.subtitle)

    def item_start_datetime(self, item):
        return item.event_start_time_utc

    def item_end_datetime(self, item):
        return item.event_end_time_utc

    def item_link(self, item):
        return item.url
