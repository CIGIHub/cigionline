---
description: "Use when working on event registration, registrants, invites, email templates, registration forms, or anything in the events/ app."
applyTo: "events/**"
---

# Events App — Registration System

See `docs/registration-system.md` for the full architecture guide.

## Model Relationships
- `EventPage` owns `RegistrationType` (Orderable), `Invite` (Orderable), and links to `RegistrationFormTemplate`
- `Registrant` belongs to one `RegistrationType` on one `EventPage`, optionally to a `RegistrationGroup`
- `RegistrationGroup` groups a primary + guests; has its own `manage_token_hash`
- `EmailCampaign` targets registrants filtered by status/type; `EmailCampaignSend` tracks delivery (unique constraint = idempotency)

## Dynamic Form Answers Storage
Answers are stored in `Registrant.answers` JSONField with these key patterns:
- Standard field: `f_<field_key>` → value
- `conditional_text`: `f_<key>__enabled` (bool) + `f_<key>__details` (text)
- `conditional_dropdown_other`: `f_<key>` (selected string) + `f_<key>__other` (textbox)
- `conditional_multiselect_other`: `f_<key>` (list of strings) + `f_<key>__other` (textbox)
- File uploads: Document IDs in `Registrant.uploaded_document_ids` JSONField (list)

## Adding a New Registration Field Type
All 10 places must be updated together — see `docs/registration-system.md` for the full checklist:
1. `events/models.py` — add `FIELD_CHOICES` entry on `RegistrationFormField`
2. `events/migrations/` — `AlterField` migration for `field_type` choices
3. `events/forms.py` — build Django field, widget attrs, storage keys, validation in `build_dynamic_form()`
4. `events/reporting.py` — columns, table formatting, CSV handling
5. `events/wagtail_hooks.py` — admin edit prefill/save if storage shape changes
6. `cigionline/static/js/admin/registration_fields_admin.js` — admin template editor + answer form
7. `cigionline/static/pages/event_page/index.js` — public form behavior + guest form clones
8. `templates/events/includes/_field.html` or `templates/events/admin/registrant_edit_answers.html`
9. `events/emailing.py` — if email output needs special formatting
10. `events/tests.py` — form validation, storage, and report display

## Registrant Status Flow
`PENDING` → `CONFIRMED` (via confirm link or direct) or `WAITLISTED` (capacity full)
`WAITLISTED` → `CONFIRMED` (auto-promoted when another cancels, via `unregister_registrant_view`)
Any → `CANCELLED`

## Security Patterns
- Self-service manage links use `manage_token_hash` (SHA256). Never store raw tokens.
- `get_registrant_for_manage_link()` / `get_group_for_manage_link()` enforce hash match; raise 404 on mismatch.
- Invite tokens are URL-safe, stored plaintext in `Invite.token`; always validate `is_valid()` and `allows_type_slug()`.
- Registration report pages are password-gated; hash stored via `make_password()` in `forms_admin.py`.

## Email Sending
- All transactional email goes through `events/emailing.py` via SendGrid API
- Render email body with `render_streamfield_email_html(template_obj, ctx)` → `(html, text)` tuple
- CSS is inlined via Premailer in `email_rendering.py`
- Never send email directly from views — always use the functions in `emailing.py`

## Key Registration Routes on EventPage
All are `@route(...)` decorated methods:
- `register_entry` — validates invite, shows type selection
- `register_form` — handles POST, creates Registrant/Group, sends pending confirmation
- `manage_registration` — self-service edit/cancel (token-gated)
- `confirm_registration` / `confirm_group_registration` — finalises pending registrations
- `registration_report` / `registration_report_type` — public password-gated reports
