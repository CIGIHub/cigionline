from __future__ import annotations
from django.conf import settings
from django.db import transaction
from wagtail.documents.models import Document
from django.apps import apps
from datetime import date, datetime, time
from decimal import Decimal
from django.core.files.uploadedfile import UploadedFile
import hashlib
import logging

logger = logging.getLogger('cigionline')


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


def _try_mailchimp_optin(email, first_name, last_name, answers, form_template, mailchimp_tag=""):
    """Subscribe to Mailchimp if any mailchimp_optin field (or legacy opt-in radio) is answered 'Yes'."""
    api_key = getattr(settings, 'MAILCHIMP_API_KEY', None)
    mc_server = getattr(settings, 'MAILCHIMP_DATA_CENTER', None)
    list_id = getattr(settings, 'MAILCHIMP_NEWSLETTER_LIST_ID', None)
    if not (api_key and mc_server and list_id) or not email:
        return

    if not form_template:
        return

    should_subscribe = False
    merge_fields_extra = {}
    for ff in form_template.fields.all():
        is_optin_type = ff.field_type == "mailchimp_optin"
        is_legacy = (
            ff.field_type == "radio"
            and "opt-in communications" in ff.label.lower()
        )
        if is_optin_type or is_legacy:
            field_key = f"f_{ff.field_key}"
            value = (answers.get(field_key) or "").strip().lower()
            if value == "yes":
                should_subscribe = True
        label_lower = ff.label.strip().lower()
        field_key = f"f_{ff.field_key}"
        val = (answers.get(field_key) or "")
        if isinstance(val, str):
            val = val.strip()
        if val and label_lower in ("job title", "jobtitle"):
            merge_fields_extra["JOBTITLE"] = val
        elif val and label_lower in ("organization", "organisation"):
            merge_fields_extra["ORG"] = val

    if not should_subscribe:
        return

    try:
        import mailchimp_marketing as MailchimpMarketing
        from mailchimp_marketing.api_client import ApiClientError

        email_lower = email.strip().lower()
        subscriber_hash = hashlib.md5(email_lower.encode("utf-8")).hexdigest()
        merge_fields = {
            "FNAME": first_name,
            "LNAME": last_name,
            **merge_fields_extra,
        }
        member_info = {
            "email_address": email_lower,
            "merge_fields": merge_fields,
            "status_if_new": "subscribed",
        }
        client = MailchimpMarketing.Client()
        client.set_config({"api_key": api_key, "server": mc_server})
        local, _, domain = email_lower.partition("@")
        masked_email = f"{local[:2]}***@{domain}" if len(local) > 2 else f"***@{domain}"
        logger.info(
            "Mailchimp opt-in attempt: email=%s list_id=%s",
            masked_email, list_id,
        )
        response = client.lists.set_list_member(list_id, subscriber_hash, member_info)
        logger.info(
            "Mailchimp opt-in response: email=%s status=%s id=%s",
            masked_email,
            response.get("status"),
            response.get("id"),
        )
        tags = [t.strip() for t in (mailchimp_tag or "").split(",") if t.strip()]
        default_tag = getattr(settings, 'MAILCHIMP_DEFAULT_TAG', '')
        if default_tag and default_tag not in tags:
            tags.append(default_tag)
        if tags:
            client.lists.update_list_member_tags(
                list_id,
                subscriber_hash,
                {"tags": [{"name": t, "status": "active"} for t in tags]},
            )
            logger.info("Mailchimp opt-in tags applied: email=%s tags=%s", masked_email, tags)
    except Exception as exc:
        local, _, domain = (email or "").lower().partition("@")
        masked_email = f"{local[:2]}***@{domain}" if len(local) > 2 else f"***@{domain}"
        logger.error(f"Mailchimp opt-in error for {masked_email}: {exc}")


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

    form_template = getattr(event, 'registration_form_template', None)
    _try_mailchimp_optin(email, first, last, cleaned, form_template, mailchimp_tag=getattr(event, 'mailchimp_tag', ''))

    return registrant
