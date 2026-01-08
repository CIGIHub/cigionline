from __future__ import annotations
from django.db import transaction
from wagtail.documents.models import Document
from django.apps import apps


def save_registrant_from_form(event, reg_type, form, invite=None):
    Registrant = apps.get_model('events', 'Registrant')

    cleaned = form.cleaned_data.copy()
    first = cleaned.pop("first_name", "")
    last = cleaned.pop("last_name", "")
    email = cleaned.pop("email", "")

    if invite and getattr(invite, "email", None):
        email = invite.email

    uploaded_doc_ids = []
    # convert uploaded files to Wagtail Documents
    for key, val in list(cleaned.items()):
        if hasattr(val, "read"):
            doc = Document.objects.create(title=getattr(val, "name", "upload"), file=val)
            uploaded_doc_ids.append(doc.id)
            cleaned[key] = {"document_id": doc.id, "name": getattr(val, "name", "upload")}

    with transaction.atomic():
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
