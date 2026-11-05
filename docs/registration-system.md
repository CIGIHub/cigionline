# Event Registration System Map

This guide maps the event registration system for future AI agents and maintainers.

## Core Models

- `events/models.py`
  - `EventPage`: owns registration routes, registration settings, registration report routes, and page rendering.
  - `RegistrationType`: per-event registration options, capacity, group registration settings, and email template overrides.
  - `RegistrationFormTemplate`: reusable container for custom registration questions.
  - `RegistrationFormField`: one dynamic question in a template. `field_type` controls how `events/forms.py` builds the runtime form.
  - `Registrant`: stores submitted identity fields and dynamic answers in `answers` JSON.
  - `RegistrationGroup`: links primary and guest registrants for group registrations.
  - `Invite`: private/invite-only registration access and use limits.

## Dynamic Form Building

- `events/forms.py`
  - `build_dynamic_form(...)` converts `RegistrationFormField` rows into a Django `Form` class.
  - Standard dynamic answers are stored under `f_<field_key>`.
  - `conditional_text` stores:
    - `f_<field_key>__enabled`
    - `f_<field_key>__details`
  - `conditional_dropdown_other` stores:
    - `f_<field_key>` as one selected string
    - `f_<field_key>__other` as the textbox value
  - `conditional_multiselect_other` stores:
    - `f_<field_key>` as a list of selected strings
    - `f_<field_key>__other` as the textbox value
  - Conditional requiredness is enforced in the dynamic form `clean()` method.

## Submission And Storage

- `events/utils.py`
  - `save_registrant_from_form(...)` creates `Registrant` records from valid forms.
  - `_jsonable(...)` converts form values, dates, decimals, uploads, lists, and dicts before storing them in JSON.

- `events/models.py`
  - `EventPage.register_form(...)` handles public registration POSTs, duplicate registration checks, invite usage, group registration creation, and pending confirmation redirects.
  - `EventPage.manage_registration(...)` builds the self-service edit form and pre-populates answers.
  - `EventPage.manage_registration_update(...)` validates and saves self-service answer edits.
  - `EventPage.confirm_registration(...)` and `EventPage.confirm_group_registration(...)` finalize pending registrations.

- `events/guest_registration.py`
  - `build_primary_and_guest_forms(...)` builds the primary form and optional guest formset.
  - Guest forms can omit fields marked `exclude_from_guest_forms`.

## Templates

- `templates/events/registration_form.html`
  - Public registration form, including optional guest formset and guest prototype.

- `templates/events/registration_manage.html`
  - Self-service single registrant edit/cancel form.

- `templates/events/registration_manage_group.html`
  - Self-service group registration management list.

- `templates/events/includes/_field.html`
  - Shared public field renderer. It reads widget attributes such as `data-conditional-toggle`, `data-conditional-select`, and `data_conditional_details_for`.

- `templates/events/admin/registrant_edit_answers.html`
  - Wagtail admin dynamic-answer edit view.

## Frontend JavaScript

- `cigionline/static/pages/event_page/index.js`
  - Public registration UX.
  - Handles file name display, modal behavior, guest form cloning, and conditional field show/hide.
  - Conditional select logic checks both single-select and multi-select widgets.

- `cigionline/static/js/admin/registration_fields_admin.js`
  - Wagtail admin registration-template editor UX.
  - Shows/hides conditional settings based on `RegistrationFormField.field_type`.
  - Also drives conditional show/hide on the Wagtail admin registrant answer edit form.

## Admin And Reports

- `events/wagtail_hooks.py`
  - Registers Wagtail admin viewsets for events, registrants, invites, registration reports, form templates, and email tools.
  - `RegistrantViewSet.edit_answers_view(...)` lets admins edit labelled dynamic answers.
  - `RegistrationReportViewSet` routes admin registration reports and CSV exports.
  - `registration_fields_admin_js()` injects the admin registration JavaScript globally.

- `events/reporting.py`
  - Shared reporting helpers used by Wagtail admin reports and public report pages.
  - `build_answer_columns(...)` maps form fields to report columns.
  - `attach_answer_cells(...)` formats table cells.
  - `registrants_csv_response(...)` exports event/type registrants to CSV.

- `templates/events/admin/registration_report_*.html`
  - Wagtail admin report views.

- `templates/events/registration_report_*.html`
  - Public password-gated registration report views.

## Email Rendering

- `events/emailing.py`
  - Sends pending confirmation, duplicate/manage, group, cancellation, reminder, and campaign-related emails.
  - `_render_registrant_answers(...)` formats `Registrant.answers` for email merge variables.

- `events/email_preview.py`
  - Builds preview data for email campaign admin UI.

- `templates/events/emails/`
  - Shared email wrappers and answer snippets.

## Tests

- `events/tests.py`
  - Existing coverage for duplicate registrations, guest exclusion, group double opt-in, and conditional multiselect "Other" behavior.

## Adding A New Registration Field Type

Update these places together:

1. `events/models.py`: add the `RegistrationFormField.FIELD_CHOICES` option.
2. `events/migrations/`: add an `AlterField` migration for `field_type` choices.
3. `events/forms.py`: build the Django field, widget attributes, storage keys, and validation.
4. `events/reporting.py`: add report columns, table formatting, and CSV handling.
5. `events/wagtail_hooks.py`: update admin edit prefill or save behavior if the storage shape changes.
6. `cigionline/static/js/admin/registration_fields_admin.js`: update Wagtail template editor visibility and admin answer form behavior.
7. `cigionline/static/pages/event_page/index.js`: update public form behavior, including guest form clones.
8. `templates/events/includes/_field.html` or `templates/events/admin/registrant_edit_answers.html`: update rendering if widget attributes are not enough.
9. `events/emailing.py`: update answer labels/formatting if email output needs special treatment.
10. `events/tests.py`: add form validation, storage, and report-display coverage.
