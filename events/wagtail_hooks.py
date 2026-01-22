from utils.admin_utils import title_with_actions, live_icon
from wagtail.admin.ui.tables import Column
from wagtail.admin.widgets import AdminPageChooser
from wagtail.admin.viewsets.base import ViewSet, ViewSetGroup
import csv
from .models import Invite, Registrant, EventListPage, EventPage, RegistrationFormTemplate
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.utils.text import slugify
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from wagtail import hooks
from wagtail.documents.models import Document
from wagtail.admin.viewsets.model import ModelViewSet


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
                "id": rtype.pk,
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

        def _abs_url(url: str) -> str:
            if not url:
                return ""
            return url if url.startswith("http://") or url.startswith("https://") else request.build_absolute_uri(url)

        def _fmt(val):
            if val is None:
                return ""
            if isinstance(val, (list, tuple)):
                return "; ".join(str(v) for v in val)
            if isinstance(val, bool):
                return "Yes" if val else "No"
            if isinstance(val, dict):
                if "name" in val:
                    return val.get("name") or ""
                return "; ".join(f"{k}={v}" for k, v in val.items())
            return str(val)

        registrants = (
            Registrant.objects
            .filter(event=event)
            .select_related("registration_type", "invite")
            .only("id", "created_at", "status", "first_name", "last_name", "email", "registration_type__name", "registration_type__slug", "answers", "invite_id", "invite__email")
            .order_by("created_at")
        )

        form_fields = list(event.registration_form_template.fields.all().order_by("sort_order"))
        file_fields = [ff for ff in form_fields if ff.field_type == "file"]

        header = [
            "Registrant ID",
            "Created",
            "Status",
            "Registration Type",
            "Type Slug",
            "First Name",
            "Last Name",
            "Email",
            "Invited?",
            "Invite Email",
        ]

        for ff in form_fields:
            if ff.field_type != "file":
                header.append(ff.label)

        for ff in file_fields:
            header.append(f"{ff.label} (file url)")

        # CSV response (with BOM so Excel handles UTF-8)
        filename = f"{slugify(event.title)}-registrants-{timezone.now().date().isoformat()}.csv"
        resp = HttpResponse(content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        resp.write("\ufeff")  # UTF-8 BOM for Excel
        writer = csv.writer(resp)
        writer.writerow(header)

        for r in registrants:
            base_row = [
                r.pk,
                getattr(r, "created_at", "") or "",
                getattr(r, "status", ""),
                getattr(r.registration_type, "name", ""),
                getattr(r.registration_type, "slug", ""),
                getattr(r, "first_name", ""),
                getattr(r, "last_name", ""),
                getattr(r, "email", ""),
                "Yes" if getattr(r, "invite_id", None) else "No",
                getattr(r.invite, "email", "") if getattr(r, "invite_id", None) else "",
            ]

            answers = getattr(r, "answers", {}) or {}

            non_file_cells = []
            for ff in form_fields:
                if ff.field_type == "file":
                    continue
                key = f"f_{ff.field_key}"
                val = answers.get(key)
                non_file_cells.append(_fmt(val))

            file_url_cells = []
            for ff in file_fields:
                url = ""
                key = f"f_{ff.field_key}"
                val = answers.get(key)
                meta = (answers or {}).get(val) or {}
                if isinstance(meta, dict):
                    doc_id = meta.get("document_id")
                    if doc_id:
                        doc = Document.objects.filter(pk=doc_id).only("id", "file").first()
                        if doc and getattr(doc.file, "url", None):
                            url = _abs_url(doc.file.url)

                file_url_cells.append(url)

            writer.writerow(base_row + non_file_cells + file_url_cells)

        return resp

    def type_registrants_view(self, request, pk: int, type_id: int):
        def _fmt_answer(val, field_type: str):
            if val is None:
                return ""
            if isinstance(val, bool):
                return "Yes" if val else "No"
            if isinstance(val, (list, tuple)):
                return "; ".join(str(v) for v in val)
            if isinstance(val, dict):
                # file field stored like {"document_id": 123, "name": "x.pdf"}
                if field_type == "file":
                    return val.get("name") or ""
                return "; ".join(f"{k}={v}" for k, v in val.items())
            return str(val)

        event = get_object_or_404(EventPage.objects.specific(), pk=pk)
        rtype = get_object_or_404(event.registration_types, pk=type_id)

        q = (request.GET.get("q") or "").strip()
        status = (request.GET.get("status") or "").strip().lower()  # e.g., confirmed|waitlisted|pending

        registrants = (
            Registrant.objects
            .filter(event=event, registration_type=rtype)
            .select_related("invite")
            .order_by("-created_at")
        )
        if q:
            registrants = registrants.filter(
                Q(email__icontains=q) |
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q)
            )
        if status in {"confirmed", "waitlisted", "pending"}:
            registrants = registrants.filter(status=status)

        form_fields = list(event.registration_form_template.fields.all().order_by("sort_order"))

        columns = []
        for ff in form_fields:
            base = f"f_{ff.field_key}"

            if ff.field_type == "conditional_text":
                columns.append({
                    "label": ff.label,
                    "type": "conditional_text",
                    "key_enabled": f"{base}__enabled",
                    "key_details": f"{base}__details",
                })
            else:
                columns.append({
                    "label": ff.label,
                    "type": ff.field_type,
                    "key": base,
                })

        paginator = Paginator(registrants, 50)
        page_obj = paginator.get_page(request.GET.get("p", 1))

        doc_ids = set()
        for r in page_obj.object_list:
            ans = r.answers or {}
            for col in columns:
                if col["type"] == "file":
                    meta = ans.get(col["key"]) or {}
                    if isinstance(meta, dict) and meta.get("document_id"):
                        doc_ids.add(meta["document_id"])

        docs_by_id = {
            d.id: d
            for d in Document.objects.filter(id__in=doc_ids).only("id", "file", "title")
        }

        for r in page_obj.object_list:
            ans = r.answers or {}
            cells = []

            for col in columns:
                # --- CONDITIONAL TEXT (checkbox + details) ---
                if col["type"] == "conditional_text":
                    enabled = bool(ans.get(col["key_enabled"]))
                    details = (ans.get(col["key_details"]) or "").strip()

                    cells.append({
                        "text": (details or "Yes") if enabled else "",
                        "url": "",
                    })
                    continue

                # --- NORMAL FIELDS ---
                val = ans.get(col["key"])

                # file field: answers store {"document_id":..., "name":...}
                if col["type"] == "file" and isinstance(val, dict) and val.get("document_id"):
                    doc = docs_by_id.get(val["document_id"])
                    cells.append({
                        "text": val.get("name") or (doc.title if doc else ""),
                        "url": (doc.file.url if doc and getattr(doc.file, "url", None) else ""),
                    })
                else:
                    cells.append({
                        "text": _fmt_answer(val, col["type"]),
                        "url": "",
                    })

            r.answer_cells = cells
            r.invited = bool(getattr(r, "invite_id", None))
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
                "columns": columns,
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
    ]
    search_fields = ('title',)
    ordering = ['title']


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
        RegistrationFormTemplate
    )


@hooks.register('register_admin_viewset')
def register_event_viewsets():
    return EventViewSetGroup()
