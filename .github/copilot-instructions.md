# Project: CIGI Online (cigionline)

## Overview
A Wagtail (Django) CMS-based website for the Centre for International Governance Innovation (CIGI). The frontend uses Webpack, React, and SCSS. It's deployed on Heroku with PostgreSQL, Elasticsearch (Bonsai), and AWS S3 for static/media files.

## Key Architecture
- **Backend**: Python/Django + Wagtail CMS. Each content type lives in its own Django app (e.g. `articles/`, `events/`, `publications/`, `people/`, `research/`).
- **Frontend**: Webpack bundles in `src/`, SCSS styles, React components for interactive UI.
- **Templates**: Jinja2/Django templates in `templates/`, organized by app.
- **Settings**: Environment-specific settings in `cigionline/settings/`.
- **Static files**: Collected to S3 (`cigionline-static-production` / `cigionline-static-staging`).

## Apps of Note
- `core/` — Shared base models, mixins, common page types
- `events/` — Event pages, guest registration, email rendering
- `articles/` — Article pages, rich text, TTS
- `people/` — Person pages
- `publications/` / `research/` — Publication and research pages
- `streams/` — StreamField blocks shared across content types
- `menus/` — Site navigation models
- `search/` — Elasticsearch-powered search

## Development
- **Virtual env**: `source venv/bin/activate`
- **Run locally**: `python manage.py runserver`
- **Run tests**: `python -m pytest` or `python manage.py test`
- **Migrations**: `python manage.py makemigrations && python manage.py migrate`
- **Frontend**: `npm run dev` (webpack watch) or `npm run build`

## Deployment (Heroku)
- **Staging**: `cigionline-staging`, `cigionline-staging-2`, `cigionline-staging-3`
- **Production**: `cigionline-production`
- **Admin**: `cigionline-admin`
- Push a branch to staging: `git push heroku <branch>:master`
- Restore production DB to staging: `heroku pg:backups:restore cigionline-production::<backup_id> DATABASE_URL --app cigionline-staging`
- Sync static files: `aws s3 sync s3://cigionline-static-production s3://cigionline-static-staging`

## Conventions
- Wagtail page models inherit from base classes in `core/models.py`
- StreamField blocks are defined/reused via `streams/`
- Wagtail hooks (admin customizations) are in each app's `wagtail_hooks.py`
- Tests use pytest and live in each app's `tests.py`
- New content type fields generally need both a migration and a template update

## Event Registration System (`events/`)

See `docs/registration-system.md` for the full architecture guide.

### Key Models
- **`EventPage`** — RoutablePage with registration sub-routes (`register_entry`, `register_form`, `manage_registration`, `confirm_registration`, etc.). Key fields: `registration_open`, `is_private_registration`, `registration_form_template`, `confirmation_template`, `waitlist_template`, `reminder_template`.
- **`RegistrationType`** (Orderable on EventPage) — Defines capacity, slug, `allow_group_registrations`, `max_guest_registrations`, `close_date`, per-type email template overrides.
- **`Registrant`** — Core record. `status` choices: `PENDING`, `CONFIRMED`, `WAITLISTED`, `CANCELLED`. Dynamic answers stored in `answers` JSONField as `f_<field_key>` (with `__details`, `__other`, `__enabled` suffixes for conditional fields). File upload Document IDs in `uploaded_document_ids` JSONField. Self-service managed via `manage_token_hash` (SHA256).
- **`RegistrationGroup`** — Groups a primary registrant + guests. Has its own `manage_token_hash`.
- **`Invite`** — URL-safe token granting access to private registrations. Fields: `token`, `email`, `max_uses`, `used_count`, `expires_at`, `allowed_type_slugs`.
- **`RegistrationFormTemplate`** / **`RegistrationFormField`** — Snippet-based reusable form builder. Fields support `visible_rule`/`required_rule` (`all`, `only`, `except`) scoped to type slugs. Custom field types: `conditional_text`, `conditional_dropdown_other`, `conditional_multiselect_other`, `mailchimp_optin`.
- **`EmailTemplate`** — StreamField-based email template (snippet). Rendered to `(html, text)` tuple via `email_rendering.py`. Supports merge vars.
- **`EmailCampaign`** / **`EmailCampaignSend`** — Scheduled bulk emails to filtered registrant sets. `EmailCampaignSend` enforces idempotency (unique constraint on campaign+registrant).

### Key Modules
- **`forms.py`** — `build_dynamic_form()` builds a Django Form class from `RegistrationFormField` rules at runtime.
- **`guest_registration.py`** — `build_primary_and_guest_forms()` produces primary form + guest formset for group registrations.
- **`registrant_management.py`** — Token-authenticated lookups for self-service manage links (`get_registrant_for_manage_link`, `get_group_for_manage_link`).
- **`emailing.py`** — All transactional email sending via SendGrid API (`send_confirmation_email`, `send_event_campaign_email`, etc.).
- **`email_rendering.py`** — Renders `EmailTemplate` StreamField bodies to `(html, text)` tuples; inlines CSS via Premailer.
- **`forms_admin.py`** — `EventPageAdminForm` handles registration report password hashing (`make_password()`).

### Admin
- `RegistrantViewSet` exposes `edit_answers_view` for editing dynamic answers + file uploads.
- `RegistrationReportViewSet` provides capacity reports, per-type registrant lists, CSV export, and admin unregister (auto-promotes next waitlisted registrant).
- `InviteViewSet` manages invite tokens (auto-generates token if blank).
