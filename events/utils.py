from __future__ import annotations
from django.db import transaction
from wagtail.documents.models import Document
from django.apps import apps
from datetime import date, datetime, time
from decimal import Decimal
from django.core.files.uploadedfile import UploadedFile


def _jsonable(value):
    """Make form values safe to stash in a JSONField/TextField."""
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, UploadedFile):
        return {"name": value.name}
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


def save_registrant_from_form(event, reg_type, form, invite=None):
    Registrant = apps.get_model('events', 'Registrant')

    # IMPORTANT: keep file -> Document creation and Registrant creation in the
    # same transaction so we don't leave orphaned Document rows if anything fails.
    with transaction.atomic():
        cleaned = form.cleaned_data.copy()
        first = cleaned.pop("first_name", "")
        last = cleaned.pop("last_name", "")
        email = cleaned.pop("email", "")

        cleaned.pop("website", None)  # honeypot field

        if invite and getattr(invite, "email", None):
            email = invite.email

        uploaded_doc_ids = []
        # Convert uploaded files to Wagtail Documents.
        for key, val in list(cleaned.items()):
            if hasattr(val, "read"):
                doc = Document.objects.create(
                    title=getattr(val, "name", "upload"),
                    file=val,
                )
                uploaded_doc_ids.append(doc.id)
                cleaned[key] = {
                    "document_id": doc.id,
                    "name": getattr(val, "name", "upload"),
                }

        cleaned = _jsonable(cleaned)

        registrant = Registrant.objects.create(
            event=event,
            registration_type=reg_type,
            email=email,
            first_name=first,
            last_name=last,
            answers=cleaned,
            uploaded_document_ids=uploaded_doc_ids,
            invite=invite,
            status="pending",
        )
        return registrant
