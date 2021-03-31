from .models import EventPage, EventListPage
from wagtail.contrib.modeladmin.options import (ModelAdmin, modeladmin_register, ModelAdminGroup)


class EventListPageAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = EventListPage
    menu_label = 'Event Landing Page'
    menu_icon = 'date'
    menu_order = 100
    list_display = ('title',)


class EventPageAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = EventPage
    menu_label = 'Events'
    menu_icon = 'date'
    menu_order = 101
    list_display = ('title', 'event_type', 'publishing_date', 'event_end', 'live')
    list_filter = ('publishing_date', 'live')
    search_fields = ('title', 'event_type',)
    ordering = ['-publishing_date']


class EventGroup(ModelAdminGroup):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    menu_label = 'Events'
    menu_icon = 'date'
    menu_order = 105
    items = (EventListPageAdmin, EventPageAdmin)


modeladmin_register(EventGroup)
