from django import forms
from .models import Invite, Registrant, EventListPage, EventPage
from wagtail import hooks
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.admin.viewsets.pages import PageListingViewSet
from wagtail.admin.viewsets.base import ViewSetGroup
from wagtail.admin.widgets import AdminPageChooser
from wagtail.admin.ui.tables import Column
from utils.admin_utils import title_with_actions, live_icon


class EventPageListingViewSet(PageListingViewSet):
    model = EventPage
    menu_label = 'Events'
    menu_icon = 'date'
    menu_order = 101
    name = 'eventpage'
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
        Column('publishing_date', label='Publishing Date', sort_key='publishing_date'),
        Column('event_type', label='Event Type', sort_key='event_type'),
        Column(live_icon, label='Live', sort_key='live'),
        Column('id', label='ID', sort_key='id'),
    ]
    list_filter = ['publishing_date', 'event_type', 'live']
    search_fields = ('title',)
    ordering = ['-publishing_date']

    def get_index_view_kwargs(self):
        kwargs = super().get_index_view_kwargs()
        kwargs["queryset"] = self.model.objects.filter(publishing_date__isnull=False)
        return kwargs


class EventListPageListingViewSet(PageListingViewSet):
    model = EventListPage
    menu_label = 'Events Landing Page'
    menu_icon = 'home'
    menu_order = 100
    name = 'eventlistpage'
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


class InviteViewSet(ModelViewSet):
    model = Invite
    icon = "lock-open"
    menu_label = "Invites"
    menu_order = 10

    list_display = (
        "token",
        "event",
        "email",
        "allowed_rule",
        "allowed_type_slugs",
        "max_uses",
        "used_count",
        "expires_at",
        "created_at",
    )
    search_fields = ("token", "email", "event__title")
    ordering = "-created_at"
    inspect_view_enabled = True
    # Nice field order in the create/edit form
    form_fields = [
        "event",
        "email",
        "allowed_rule",
        "allowed_type_slugs",
        "max_uses",
        "expires_at",
        # token & used_count are auto/managed; expose token if you want to copy it
        # "token",
    ]
    
    form_widgets = {
        "event": AdminPageChooser(target_models=[EventPage]),  # or target_model=EventPage
    }


    def form_valid(self, form):
        obj = form.instance
        if not getattr(obj, "token", None):
            import secrets
            obj.token = secrets.token_urlsafe(24)
        return super().form_valid(form)


class RegistrantViewSet(ModelViewSet):
    model = Registrant
    icon = "user"
    menu_label = "Registrants"
    menu_order = 20

    list_display = (
        "email",
        "event",
        "registration_type",
        "status",
        "created_at",
    )
    search_fields = ("email", "event__title", "registration_type__name")
    ordering = "-created_at"

    # Helpful filter columns (keep simple for reliability)
    list_filter = ("status", "registration_type")  # editors can drill down fast

    # Fields you want editable in admin (answers are usually read-only)
    form_fields = [
        "event",
        "registration_type",
        "email",
        "first_name",
        "last_name",
        "status",
        # Show read-only blobs if you want:
        # "answers",
        # "uploaded_document_ids",
        # "invite",
    ]


class EventsAdminGroup(ViewSetGroup):
    menu_label = "Event Registrations"
    menu_icon = "date"       # choose any Wagtail icon
    menu_order = 300
    items = [InviteViewSet, RegistrantViewSet]


@hooks.register("register_admin_viewset")
def register_events_group():
    return EventsAdminGroup()
