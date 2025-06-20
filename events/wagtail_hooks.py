from wagtail import hooks
from .models import EventListPage, EventPage
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.admin.viewsets.base import ViewSetGroup
from wagtail.admin.ui.tables import Column
from utils.admin_utils import title_with_actions, live_icon


class EventPageListingViewSet(ModelViewSet):
    model = EventPage
    menu_label = 'Events'
    menu_icon = 'date'
    menu_order = 101
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
        Column('publishing_date', label='Publishing Date', sort_key='publishing_date'),
        Column('event_type', label='Event Type', sort_key='event_type'),
        Column(live_icon, label='Live', sort_key='live'),
        Column('id', label='ID', sort_key='id'),
    ]
    list_filter = ['publishing_date', 'event_type', 'live']
    form_fields = ['title', 'publishing_date', 'event_type']
    search_fields = ('title',)
    ordering = ['-publishing_date']

    def get_index_view_kwargs(self):
        kwargs = super().get_index_view_kwargs()
        kwargs["queryset"] = self.model.objects.filter(publishing_date__isnull=False)
        return kwargs


class EventListPageListingViewSet(ModelViewSet):
    model = EventListPage
    menu_label = 'Events Landing Page'
    menu_icon = 'home'
    menu_order = 100
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    form_fields = ['title',]
    search_fields = ('title',)
    ordering = ['title']


class EventViewSetGroup(ViewSetGroup):
    menu_label = 'Events'
    menu_icon = 'date'
    menu_order = 104
    items = (EventListPageListingViewSet, EventPageListingViewSet)


@hooks.register('register_admin_viewset')
def register_event_viewsets():
    return EventViewSetGroup()
