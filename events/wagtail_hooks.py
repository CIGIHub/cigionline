import csv
from .models import Invite, Registrant, EventListPage, EventPage
from django.urls import path
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.utils.text import slugify
from django.utils import timezone
from wagtail import hooks
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.admin.viewsets.base import ViewSet, ViewSetGroup
from wagtail.admin.widgets import AdminPageChooser
from wagtail.admin.ui.tables import Column
from wagtail import hooks
from wagtail.contrib.forms.utils import get_field_clean_name
from utils.admin_utils import title_with_actions, live_icon


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
        "answers",
        "uploaded_document_ids",
        "invite",
    ]


class RegistrationReportViewSet(ViewSet):
    icon = "table"
    menu_label = "Registration Reports"
    menu_order = 40
    add_to_admin_menu = True
    name = "registration_reports"
    url_prefix = "event-registrations/reports"

    def index_view(self, request):
        events = (
            EventPage.objects.live()
            .filter(registration_open=True)
            .specific()
            .order_by("-first_published_at")
        )

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
            })

        return TemplateResponse(
            request,
            "events/admin/registration_report_index.html",
            {
                "view": self,
                "rows": rows,
                "index_url_name": self.get_url_name("index"),
                "detail_url_name": self.get_url_name("detail"),
                "export_csv_url_name": self.get_url_name("export_csv"),
            },
        )

    def detail_view(self, request, pk: int):
        event = get_object_or_404(EventPage.objects.specific(), pk=pk)

        # Build per-type capacity metrics
        type_rows = []
        for rtype in event.registration_types.all().order_by("sort_order"):
            confirmed = rtype.registrants.filter(
                status=Registrant.Status.CONFIRMED
            ).count()
            waitlisted = rtype.registrants.filter(
                status=Registrant.Status.WAITLISTED
            ).count()
            cap = rtype.capacity  # can be None
            remaining = None if cap is None else max(cap - confirmed, 0)
            type_rows.append({
                "name": rtype.name,
                "slug": rtype.slug,
                "capacity": cap,
                "confirmed": confirmed,
                "waitlisted": waitlisted,
                "remaining": remaining,
            })

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

        # Prefetch related data to keep this fast
        registrants = (
            Registrant.objects
            .filter(event=event)
            .select_related("registration_type", "invite")
            .prefetch_related("uploads__field")   # if you added RegistrantUpload(field, file)
            .order_by("created_at")
        )

        # Build columns: base + question labels + file columns
        form_fields = list(event.form_fields.all().order_by("sort_order"))
        label_by_clean = {get_field_clean_name(ff.label): ff.label for ff in form_fields}
        file_fields = [ff for ff in form_fields if ff.field_type == "file"]

        header = [
            "Registrant ID",
            "Created",
            "Updated",
            "Status",
            "Registration Type",
            "Type Slug",
            "First Name",
            "Last Name",
            "Email",
            "Invited?",            # yes/no
            "Invite Email",        # if any
        ]
        # one column per non-file question (by label)
        for ff in form_fields:
            if ff.field_type != "file":
                header.append(ff.label)

        # file columns (name, path, url) per file-question
        for ff in file_fields:
            base = ff.label
            header.extend([f"{base} (file name)", f"{base} (file path)", f"{base} (file url)"])

        # CSV response (with BOM so Excel handles UTF-8)
        filename = f"{slugify(event.title)}-registrants-{timezone.now().date().isoformat()}.csv"
        resp = HttpResponse(content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        resp.write("\ufeff")  # UTF-8 BOM for Excel
        writer = csv.writer(resp)

        writer.writerow(header)

        # Helper to humanize answer values
        def _fmt(val):
            if val is None:
                return ""
            if isinstance(val, (list, tuple)):
                return "; ".join(str(v) for v in val)
            if isinstance(val, bool):
                return "Yes" if val else "No"
            if isinstance(val, dict):
                # e.g., {"document_id": 123, "name": "file.pdf"} from your saver
                if "name" in val:
                    return val.get("name") or ""
                return "; ".join(f"{k}={v}" for k, v in val.items())
            return str(val)

        for r in registrants:
            base_row = [
                r.pk,
                getattr(r, "created_at", "") or "",
                getattr(r, "updated_at", "") or "",
                getattr(r, "status", ""),
                getattr(r.registration_type, "name", ""),
                getattr(r.registration_type, "slug", ""),
                getattr(r, "first_name", ""),
                getattr(r, "last_name", ""),
                getattr(r, "email", ""),
                "Yes" if getattr(r, "invite_id", None) else "No",
                getattr(r.invite, "email", "") if getattr(r, "invite_id", None) else "",
            ]

            # Answers dictionary keyed by clean_name
            answers = getattr(r, "answers", {}) or {}

            # Non-file answers in label order
            answer_cells = []
            for ff in form_fields:
                if ff.field_type == "file":
                    continue
                clean = get_field_clean_name(ff.label)
                answer_cells.append(_fmt(answers.get(clean)))

            # File answers: prefer RegistrantUpload, fallback to answers dict
            upload_cells = []
            # Build a quick map of file uploads by field id
            uploads_by_field_id = {}
            for up in getattr(r, "uploads", []).all() if hasattr(r, "uploads") else []:
                if getattr(up, "field_id", None):
                    uploads_by_field_id[up.field_id] = up

            for ff in file_fields:
                name, path, url = "", "", ""
                # Prefer RegistrantUpload row
                up = uploads_by_field_id.get(ff.id)
                if up:
                    name = getattr(up, "original_name", "") or (getattr(up.file, "name", "").split("/")[-1] if getattr(up, "file", None) else "")
                    path = getattr(up.file, "name", "") if getattr(up, "file", None) else ""
                    url = getattr(up.file, "url", "") if getattr(up, "file", None) and hasattr(up.file, "url") else ""
                else:
                    # Fallback if using the answers dict document reference
                    clean = get_field_clean_name(ff.label)
                    v = answers.get(clean)
                    if isinstance(v, dict):
                        name = v.get("name", "")
                        path = f"document:{v.get('document_id')}" if v.get("document_id") else ""
                        url = ""  # could resolve Document and pull .url, but avoids extra queries
                upload_cells.extend([name, path, url])

            writer.writerow(base_row + answer_cells + upload_cells)

        return resp

    def get_urlpatterns(self):
        return [
            path("", self.index_view, name="index"),
            path("<int:pk>/", self.detail_view, name="detail"),
            path("<int:pk>/export.csv", self.export_csv_view, name="export_csv"),
        ]


class EventViewSetGroup(ViewSetGroup):
    menu_label = 'Events'
    menu_icon = 'date'
    menu_order = 104
    items = (EventListPageListingViewSet, EventPageListingViewSet, InviteViewSet, RegistrantViewSet, RegistrationReportViewSet)


@hooks.register('register_admin_viewset')
def register_event_viewsets():
    return EventViewSetGroup()
