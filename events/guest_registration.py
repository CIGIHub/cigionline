from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django import forms
from django.forms import formset_factory

from .forms import build_dynamic_form


@dataclass(frozen=True)
class GuestForms:
    primary_form: forms.Form
    guest_formset: Any


def build_primary_and_guest_forms(*, event, reg_type, invite, post_data=None, files_data=None) -> GuestForms:
    """Build the primary registration form and an optional guest formset.

    - Guests are only enabled when event.allow_guest_registrations is True.
    - Max guests enforced by event.max_guest_registrations (default 5).
    - Guests share the primary email; guest forms do not include email nor honeypot.
    """

    primary_form_class = build_dynamic_form(event, reg_type, invite)

    # Primary form binds normally.
    primary_form = primary_form_class(post_data, files_data) if post_data is not None else primary_form_class()

    if not getattr(event, "allow_guest_registrations", False):
        guest_formset = None
        return GuestForms(primary_form=primary_form, guest_formset=guest_formset)

    max_guests = int(getattr(event, "max_guest_registrations", 5) or 5)
    max_guests = max(0, min(max_guests, 25))  # sanity cap

    guest_form_class = build_dynamic_form(
        event,
        reg_type,
        invite,
        require_email=False,
        include_honeypot=False,
    )

    # Guests share the primary email; remove the email field entirely.
    if "email" in guest_form_class.base_fields:
        guest_form_class.base_fields.pop("email")

    # On GET (unbound), render one empty form so the template always includes
    # proper formset management fields + a usable prototype even if JS is disabled.
    extra = 0 if post_data is not None else 1

    GuestFormSet = formset_factory(
        guest_form_class,
        extra=extra,
        max_num=max_guests,
        validate_max=True,
    )

    guest_formset = GuestFormSet(post_data, files_data, prefix="guests") if post_data is not None else GuestFormSet(prefix="guests")

    return GuestForms(primary_form=primary_form, guest_formset=guest_formset)
