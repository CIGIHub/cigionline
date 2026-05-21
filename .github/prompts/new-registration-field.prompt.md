---
description: "Add a new registration form field type to the event registration system — all 10 required changes"
argument-hint: "Describe the new field type and its behaviour"
agent: "agent"
---

Add a new registration form field type to the event registration system.

## What to build

$input

## All 10 required changes (must all be done together)

See `docs/registration-system.md` for the full architecture guide.

### 1. `events/models.py`
Add a new entry to `RegistrationFormField.FIELD_CHOICES` (or the `field_type` CharField choices). Follow the existing naming pattern (lowercase, underscored).

### 2. `events/migrations/`
Generate an `AlterField` migration for the `field_type` choices change:
```
python manage.py makemigrations events
```
Review the generated migration to confirm it's an `AlterField` on `RegistrationFormField.field_type`.

### 3. `events/forms.py`
In `build_dynamic_form()`:
- Add the new field type to `WAGTAIL_FIELD_MAP` or handle it explicitly
- Build the appropriate Django form field and widget
- Set widget CSS classes (`cigi-input`, `cigi-select`, `cigi-file-input`, etc.) and any `data-*` attributes for frontend conditional logic
- Define the storage key(s) — standard: `f_<field_key>`, conditional variants add `__enabled`, `__details`, `__other` suffixes
- Add any `clean()` validation logic needed

### 4. `events/reporting.py`
- Add column definition in `build_answer_columns()`
- Add cell formatting in `attach_answer_cells()`
- Handle the value in `registrants_csv_response()` if CSV export needs special treatment

### 5. `events/wagtail_hooks.py`
- Update `RegistrantViewSet.edit_answers_view()` prefill logic if the storage shape is non-standard
- Update save logic to correctly persist the new field's answer keys

### 6. `cigionline/static/js/admin/registration_fields_admin.js`
- Add the new field type to the visibility rules for the Wagtail template editor (show/hide conditional settings panels)
- Handle the new field type in the admin registrant answer edit form if it needs special UI

### 7. `cigionline/static/pages/event_page/index.js`
- Add public form behaviour (show/hide, conditional logic)
- Ensure guest form cloning correctly handles the new field

### 8. Template rendering
- If widget attributes alone are insufficient, update `templates/events/includes/_field.html` (public forms) or `templates/events/admin/registrant_edit_answers.html` (admin)

### 9. `events/emailing.py`
- Update `_render_registrant_answers()` if the new field needs special label resolution, value formatting, or should be excluded from emails

### 10. `events/tests.py`
Add tests covering:
- Form validation (valid and invalid submissions)
- Correct storage in `Registrant.answers`
- Report column + CSV output display
- Any conditional/required logic

## Checklist before finishing
- [ ] `FIELD_CHOICES` updated in model
- [ ] Migration generated and reviewed
- [ ] `build_dynamic_form()` handles the new type
- [ ] Reporting columns + CSV updated
- [ ] Admin answer edit view handles the new type
- [ ] Admin JS shows/hides correct settings
- [ ] Public JS handles the new type
- [ ] Templates updated if needed
- [ ] Emails handle the new type
- [ ] Tests written and passing (`python -m pytest events/tests.py`)
