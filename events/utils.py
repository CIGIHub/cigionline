from django.apps import apps
from wagtail.documents.models import Document


def save_registrant_from_form(event, reg_type, form, invite=None):
    cleaned = form.cleaned_data.copy()
    first = cleaned.pop('first_name', '')
    last = cleaned.pop('last_name', '')
    email = cleaned.pop('email', '')

    # If invite email was locked, prefer invite.email
    if invite and invite.email:
        email = invite.email

    doc_ids = []
    for key, val in list(cleaned.items()):
        if hasattr(val, 'read'):  # file-like
            doc = Document.objects.create(title=val.name, file=val)
            doc_ids.append(doc.id)
            cleaned[key] = {'document_id': doc.id, 'name': val.name}

    Registrant = apps.get_model('events', 'Registrant')

    registrant = Registrant.objects.create(
        event=event,
        registration_type=reg_type,
        email=email,
        first_name=first,
        last_name=last,
        answers=cleaned,
        uploaded_document_ids=doc_ids,
        invite=invite,
        status=Registrant.Status.PENDING,
    )
    return registrant
