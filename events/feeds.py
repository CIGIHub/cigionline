from django_ical.views import ICalFeed
from events.models import EventPage
import re
import pytz


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
        '''
        - The datetime value entered in EventPage is currently assumed tzinfo="America/Toronto", 
        regardless of the "time_zone" field specified; eg. "07:00:00AM America/Los_Angelos"
        - This is then converted to UTC and stored as "publishing_date"; eg. "11:00:00 (during daylight saving)."
        - So to allow specifying different timezones for the "time_zone" field, we need to first 
        convert "publishing_date" from UTC back to "America/Toronto", then replace tzinfo with "item_zone"
        - If in the future, "publishing_date" is fixed to have user-specified timezone instead,
        this conversion and replacement would be unnecessary (and incorrect);
        can pass `return item.publishing_date` instead
        - This applies to item.event_end as well
        '''
        return item.publishing_date.astimezone(pytz.timezone('America/Toronto')).replace(tzinfo=pytz.timezone(item.time_zone))

    def item_end_datetime(self, item):
        return item.event_end.astimezone(pytz.timezone('America/Toronto')).replace(tzinfo=pytz.timezone(item.time_zone))

    def item_link(self, item):
        return item.url
