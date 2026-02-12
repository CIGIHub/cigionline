from utils.admin_utils import title_with_actions, live_icon
from wagtail.admin.ui.tables import Column
from wagtail.admin.widgets import AdminPageChooser
from wagtail.admin.viewsets.base import ViewSet, ViewSetGroup

from .models import (
    EmailTemplate,
    EmailCampaign,
    Invite,
    Registrant,
    RegistrationType,
    EventListPage,
    EventPage,
    RegistrationFormTemplate,
)

from django.db import models as dj_models

from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.utils.html import format_html

from wagtail import hooks
from wagtail.admin.viewsets.model import ModelViewSet

from .reporting import (
    attach_answer_cells,
    build_answer_columns,
    build_type_rows,
    filter_registrants_queryset,
    paginate_queryset,
    registrants_csv_response,
)


class EventPageListingViewSet(ModelViewSet):
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


class EventListPageListingViewSet(ModelViewSet):
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


class InviteViewSet(ModelViewSet):
    model = Invite
    icon = "lock-open"
    menu_label = "Invites"
    menu_order = 10

    list_display = (
        "token",
        "event",
        "email",
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
    name = "registrants"
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
        "answers",
        "uploaded_document_ids",
        "invite",
    ]


class RegistrationReportViewSet(ViewSet):
    icon = "table"
    menu_label = "Registration Reports"
    menu_order = 40
    name = "registration_reports"
    url_prefix = "event-registrations/reports"

    def index_view(self, request):
        sort = (request.GET.get("sort") or "publishing_date").strip()
        direction = (request.GET.get("dir") or "desc").strip().lower()
        q = (request.GET.get("q") or "").strip()

        sort_map = {
            "publishing_date": "publishing_date",
            "last_published_at": "last_published_at",
        }
        sort_field = sort_map.get(sort, "publishing_date")
        prefix = "-" if direction != "asc" else ""

        events_qs = EventPage.objects.live().filter(registration_open=True)
        if q:
            events_qs = events_qs.filter(title__icontains=q)

        events = events_qs.specific().order_by(f"{prefix}{sort_field}")

        rows = []
        for ev in events:
            types = list(ev.registration_types.all())
            confirmed_total = Registrant.objects.filter(
                event=ev, status=Registrant.Status.CONFIRMED
            ).count()
            rows.append({
                "event": ev,
                "type_count": len(types),
                "confirmed_total": confirmed_total,
                "publishing_date": getattr(ev, "publishing_date", None),
                "last_published_at": getattr(ev, "last_published_at", None),
            })

        return TemplateResponse(
            request,
            "events/admin/registration_report_index.html",
            {
                "view": self,
                "rows": rows,
                "sort": sort_field,
                "dir": "asc" if direction == "asc" else "desc",
                "q": q,
                "index_url_name": self.get_url_name("index"),
                "detail_url_name": self.get_url_name("detail"),
                "export_csv_url_name": self.get_url_name("export_csv"),
            },
        )

    def detail_view(self, request, pk: int):
        event = get_object_or_404(EventPage.objects.specific(), pk=pk)

        type_rows = build_type_rows(event)

        return TemplateResponse(
            request,
            "events/admin/registration_report_detail.html",
            {
                "view": self,
                "event": event,
                "type_rows": type_rows,
                "index_url_name": self.get_url_name("index"),
                "detail_url_name": self.get_url_name("detail"),
                "export_csv_url_name": self.get_url_name("export_csv"),
                "type_url_name": self.get_url_name("type_registrants"),
            },
        )

    def export_csv_view(self, request, pk: int):
        """
        Download all registrants for the event as CSV:
        - Basics: id, created, updated, status, type, first/last/email, invite info
        - One column per custom question (by label) with a human-readable value
        - One column per file-question: file name, storage path, and URL (if available)
        """
        event = get_object_or_404(EventPage.objects.specific(), pk=pk)

        registrants = (
            Registrant.objects.filter(event=event)
            .select_related("registration_type", "invite")
            .only(
                "id",
                "created_at",
                "status",
                "first_name",
                "last_name",
                "email",
                "registration_type__name",
                "registration_type__slug",
                "answers",
                "invite_id",
                "invite__email",
            )
            .order_by("created_at")
        )
        return registrants_csv_response(
            request=request,
            event=event,
            registrants_qs=registrants,
            filename_prefix=event.title,
        )

    def type_registrants_view(self, request, pk: int, type_id: int):
        event = get_object_or_404(EventPage.objects.specific(), pk=pk)
        rtype = get_object_or_404(event.registration_types, pk=type_id)

        q = (request.GET.get("q") or "").strip()
        status = (request.GET.get("status") or "").strip().lower()  # e.g., confirmed|waitlisted|pending

        registrants = filter_registrants_queryset(event=event, rtype=rtype, q=q, status=status)
        columns = build_answer_columns(event)
        page_obj = paginate_queryset(registrants, request=request, per_page=50)

        attach_answer_cells(page_obj, columns=columns)
        for r in page_obj.object_list:
            r.edit_url = reverse("registrants:edit", args=[r.pk])

        return TemplateResponse(
            request,
            "events/admin/registration_report_type.html",
            {
                "view": self,
                "event": event,
                "rtype": rtype,
                "page_obj": page_obj,
                "q": q,
                "status": status,
                "index_url_name": self.get_url_name("index"),
                "detail_url_name": self.get_url_name("detail"),
                "type_url_name": self.get_url_name("type_registrants"),
                "export_csv_url_name": self.get_url_name("export_csv"),
                "unregister_url_name": self.get_url_name("unregister"),
                "columns": [c.__dict__ for c in columns],
            },
        )

    @method_decorator(require_POST, name="unregister_registrant_view")
    def unregister_registrant_view(self, request, pk: int, registrant_id: int):
        event = get_object_or_404(EventPage.objects.specific(), pk=pk)

        if not request.user.has_perm("events.change_registrant"):
            return HttpResponse("Forbidden", status=403)

        registrant = get_object_or_404(
            Registrant.objects.select_related("registration_type"),
            pk=registrant_id,
            event=event,
        )

        if registrant.status != Registrant.Status.CANCELLED:
            old_status = registrant.status
            registrant.status = Registrant.Status.CANCELLED
            registrant.save(update_fields=["status"])
            messages.success(request, f"Unregistered ID: {registrant.pk} - {registrant.first_name} {registrant.last_name} ({registrant.email}) (was {old_status}).")

            if old_status == Registrant.Status.CONFIRMED and registrant.registration_type.capacity is not None:
                next_up = (
                    Registrant.objects
                    .filter(
                        event=event,
                        registration_type=registrant.registration_type,
                        status=Registrant.Status.WAITLISTED,
                    )
                    .order_by("created_at")
                    .first()
                )
                if next_up:
                    next_up.status = Registrant.Status.CONFIRMED
                    next_up.save(update_fields=["status"])
                    messages.success(request, f"Promoted ID: {next_up.pk} - {next_up.first_name} {next_up.last_name} ({next_up.email}) from waitlist.")
        else:
            messages.info(request, f"{registrant.email} is already cancelled.")

        # ✅ Redirect back to the same type registrants page
        url = reverse(self.get_url_name("type_registrants"), args=[event.pk, registrant.registration_type_id])
        return redirect(url)

    def get_urlpatterns(self):
        return [
            path("", self.index_view, name="index"),
            path("<int:pk>/", self.detail_view, name="detail"),
            path("<int:pk>/export.csv", self.export_csv_view, name="export_csv"),
            path("<int:pk>/type/<int:type_id>/", self.type_registrants_view, name="type_registrants"),
            path("<int:pk>/unregister/<int:registrant_id>/", self.unregister_registrant_view, name="unregister"),
        ]


class RegistrationFormTemplate(ModelViewSet):
    model = RegistrationFormTemplate
    menu_label = "Registration Form Templates"
    menu_icon = "form"
    menu_order = 105
    name = "registrationformtemplate"
    list_display = [
        'title',
        Column(
            "created_at",
            label="Created",
            sort_key="created_at",
        ),
        Column(
            "used_by_events",
            label="Used by events",
            accessor=lambda obj: EventPage.objects.filter(registration_form_template_id=obj.pk).count(),
            sort_key=None,
        ),
    ]
    search_fields = ('title',)
    ordering = ["-created_at", "title"]


class EmailTemplateViewSet(ModelViewSet):
    model = EmailTemplate
    menu_label = "Email Templates"
    menu_icon = "mail"
    menu_order = 106
    name = "emailtemplate"
    list_display = [
        Column(
            "title",
            label="Title",
            accessor=lambda obj: format_html(
                '<a href="{}">{}</a>',
                f"/admin/snippets/events/emailtemplate/edit/{obj.pk}/",
                obj.title,
            ),
        ),
        Column(
            "created_at",
            label="Created",
            sort_key="created_at",
        ),
        Column(
            "used_by_events",
            label="Used by events",
            accessor=lambda obj: (
                EventPage.objects.filter(
                    dj_models.Q(confirmation_template_id=obj.pk)
                    | dj_models.Q(waitlist_template_id=obj.pk)
                    | dj_models.Q(reminder_template_id=obj.pk)
                ).count()
                + RegistrationType.objects.filter(
                    dj_models.Q(confirmation_template_override_id=obj.pk)
                    | dj_models.Q(waitlist_template_override_id=obj.pk)
                    | dj_models.Q(reminder_template_override_id=obj.pk)
                )
                .values("event_id")
                .distinct()
                .count()
            ),
            sort_key=None,
        ),
    ]
    search_fields = ('title',)
    ordering = ["-created_at", "title"]


class EmailCampaignViewSet(ModelViewSet):
    model = EmailCampaign
    menu_label = "Email Campaigns"
    menu_icon = "mail"
    menu_order = 107
    name = "emailcampaign"

    list_display = [
        "event",
        "template",
        "scheduled_for",
        "sent_at",
        "completed_at",
    ]
    search_fields = ("event__title", "template__title")
    ordering = ["-scheduled_for"]

    form_fields = [
        "event",
        "template",
        "scheduled_for",
        "include_statuses",
        "include_type_slugs",
        "attachment",
        "sent_at",
        "completed_at",
    ]


class EventViewSetGroup(ViewSetGroup):
    menu_label = 'Events'
    menu_icon = 'date'
    menu_order = 104
    items = (
        EventListPageListingViewSet,
        EventPageListingViewSet,
        InviteViewSet,
        RegistrantViewSet,
        RegistrationReportViewSet,
        RegistrationFormTemplate,
        EmailTemplateViewSet,
        EmailCampaignViewSet,
    )


@hooks.register('register_admin_viewset')
def register_event_viewsets():
    return EventViewSetGroup()


@hooks.register("insert_global_admin_js")
def registration_fields_admin_js():
    return format_html(
        '<script src="{}"></script>',
        "/static/js/admin/registration_fields_admin.js",
    )
