"""Shared reporting helpers for registration reports.

This module is used by both:
- the Wagtail admin Registration Reports viewset (events/wagtail_hooks.py)
- the public EventRegistrationReportPage routable views (events/models.py)

Keeping this logic in one place prevents drift between admin and public reports.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import Any

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.utils.text import slugify

from wagtail.documents.models import Document

from .models import Registrant


def build_type_rows(event) -> list[dict[str, Any]]:
    """Capacity metrics by registration type (same as admin report detail)."""

    type_rows = []
    for rtype in event.registration_types.all().order_by("sort_order"):
        confirmed = rtype.registrants.filter(status=Registrant.Status.CONFIRMED).count()
        waitlisted = rtype.registrants.filter(status=Registrant.Status.WAITLISTED).count()
        cap = rtype.capacity
        remaining = None if cap is None else max(cap - confirmed, 0)
        type_rows.append(
            {
                "id": rtype.pk,
                "name": rtype.name,
                "slug": rtype.slug,
                "capacity": cap,
                "confirmed": confirmed,
                "waitlisted": waitlisted,
                "remaining": remaining,
            }
        )
    return type_rows


@dataclass(frozen=True)
class AnswerColumn:
    label: str
    type: str
    key: str | None = None
    key_select: str | None = None
    key_other: str | None = None
    key_enabled: str | None = None
    key_details: str | None = None
    trigger_value: str | None = None


def build_answer_columns(event) -> list[AnswerColumn]:
    """Return table columns for answers; matches admin type registrants view."""

    form_fields = list(event.registration_form_template.fields.all().order_by("sort_order"))
    columns: list[AnswerColumn] = []

    for ff in form_fields:
        base = f"f_{ff.field_key}"

        if ff.field_type == "conditional_dropdown_other":
            trigger = (getattr(ff, "conditional_other_value", "") or "").strip() or "Other"
            columns.append(
                AnswerColumn(
                    label=ff.label,
                    type="conditional_dropdown_other",
                    key_select=base,
                    key_other=f"{base}__other",
                    trigger_value=trigger,
                )
            )
        elif ff.field_type == "conditional_text":
            columns.append(
                AnswerColumn(
                    label=ff.label,
                    type="conditional_text",
                    key_enabled=f"{base}__enabled",
                    key_details=f"{base}__details",
                )
            )
        else:
            columns.append(AnswerColumn(label=ff.label, type=ff.field_type, key=base))

    return columns


def filter_registrants_queryset(*, event, rtype, q: str, status: str):
    registrants = (
        Registrant.objects.filter(event=event, registration_type=rtype)
        .select_related("invite")
        .order_by("-created_at")
    )
    if q:
        registrants = registrants.filter(
            Q(email__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
        )
    if status in {"confirmed", "waitlisted", "pending"}:
        registrants = registrants.filter(status=status)
    return registrants


def paginate_queryset(queryset, *, request: HttpRequest, per_page: int = 50):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("p", 1))


def _fmt_answer(val: Any, field_type: str) -> str:
    if val is None:
        return ""
    if isinstance(val, bool):
        return "Yes" if val else "No"
    if isinstance(val, (list, tuple)):
        return "; ".join(str(v) for v in val)
    if isinstance(val, dict):
        if field_type == "file":
            return val.get("name") or ""
        return "; ".join(f"{k}={v}" for k, v in val.items())
    return str(val)


def attach_answer_cells(page_obj, *, columns: list[AnswerColumn]):
    """Mutates registrants in page_obj: adds answer_cells, invited, edit_url."""

    doc_ids: set[int] = set()
    for r in page_obj.object_list:
        ans = r.answers or {}
        for col in columns:
            if col.type == "file" and col.key:
                meta = ans.get(col.key) or {}
                if isinstance(meta, dict) and meta.get("document_id"):
                    doc_ids.add(meta["document_id"])

    docs_by_id = {
        d.id: d
        for d in Document.objects.filter(id__in=doc_ids).only("id", "file", "title")
    }

    for r in page_obj.object_list:
        ans = r.answers or {}
        cells: list[dict[str, str]] = []

        for col in columns:
            if col.type == "conditional_text":
                enabled = bool(ans.get(col.key_enabled or ""))
                details = (ans.get(col.key_details or "") or "").strip()
                cells.append({"text": (details or "Yes") if enabled else "", "url": ""})
                continue

            if col.type == "conditional_dropdown_other":
                selected = (ans.get(col.key_select or "") or "").strip()
                other = (ans.get(col.key_other or "") or "").strip()
                trigger = (col.trigger_value or "Other").strip()

                if not selected:
                    text = ""
                elif selected == trigger:
                    text = f"{trigger} — {other}" if other else trigger
                else:
                    text = selected

                cells.append({"text": text, "url": ""})
                continue

            val = ans.get(col.key or "")
            if col.type == "file" and isinstance(val, dict) and val.get("document_id"):
                doc = docs_by_id.get(val["document_id"])
                cells.append(
                    {
                        "text": val.get("name") or (doc.title if doc else ""),
                        "url": (doc.file.url if doc and getattr(doc.file, "url", None) else ""),
                    }
                )
            else:
                cells.append({"text": _fmt_answer(val, col.type), "url": ""})

        r.answer_cells = cells
        r.invited = bool(getattr(r, "invite_id", None))


def registrants_csv_response(
    *,
    request: HttpRequest,
    event,
    registrants_qs,
    filename_prefix: str,
) -> HttpResponse:
    """CSV download for a registrants queryset (event-wide or per-type)."""

    def _abs_url(url: str) -> str:
        if not url:
            return ""
        return (
            url
            if url.startswith("http://") or url.startswith("https://")
            else request.build_absolute_uri(url)
        )

    def _fmt(val: Any) -> str:
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
        if ff.field_type == "file":
            continue
        if ff.field_type == "conditional_text":
            header.append(f"{ff.label} (enabled)")
            header.append(f"{ff.label} (details)")
            continue
        if ff.field_type == "conditional_dropdown_other":
            header.append(f"{ff.label} (selection)")
            header.append(f"{ff.label} (other)")
            continue
        header.append(ff.label)

    for ff in file_fields:
        header.append(f"{ff.label} (file name)")
        header.append(f"{ff.label} (file url)")

    filename = f"{slugify(filename_prefix)}-registrants-{timezone.now().date().isoformat()}.csv"
    resp = HttpResponse(content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    resp.write("\ufeff")
    writer = csv.writer(resp)
    writer.writerow(header)

    # Preload documents for any file fields
    doc_ids: set[int] = set()
    for r in registrants_qs:
        ans = getattr(r, "answers", {}) or {}
        for ff in file_fields:
            key = f"f_{ff.field_key}"
            meta = ans.get(key)
            if isinstance(meta, dict) and meta.get("document_id"):
                doc_ids.add(meta["document_id"])

    docs_by_id = {d.id: d for d in Document.objects.filter(id__in=doc_ids).only("id", "file")}

    for r in registrants_qs:
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

        non_file_cells: list[str] = []
        for ff in form_fields:
            if ff.field_type == "file":
                continue

            base_key = f"f_{ff.field_key}"
            if ff.field_type == "conditional_text":
                non_file_cells.append(_fmt(answers.get(f"{base_key}__enabled")))
                non_file_cells.append(_fmt(answers.get(f"{base_key}__details")))
                continue
            if ff.field_type == "conditional_dropdown_other":
                non_file_cells.append(_fmt(answers.get(base_key)))
                non_file_cells.append(_fmt(answers.get(f"{base_key}__other")))
                continue
            non_file_cells.append(_fmt(answers.get(base_key)))

        file_cells: list[str] = []
        for ff in file_fields:
            file_name = ""
            file_url = ""
            key = f"f_{ff.field_key}"
            val = answers.get(key)
            meta = val if isinstance(val, dict) else {}
            if meta:
                file_name = str(meta.get("name") or "")
                doc_id = meta.get("document_id")
                if doc_id:
                    doc = docs_by_id.get(doc_id)
                    if doc and getattr(doc.file, "url", None):
                        file_url = _abs_url(doc.file.url)
            file_cells.append(file_name)
            file_cells.append(file_url)

        writer.writerow(base_row + non_file_cells + file_cells)

    return resp
