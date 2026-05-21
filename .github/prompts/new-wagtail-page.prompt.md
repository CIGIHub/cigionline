---
description: "Scaffold a new Wagtail page type — model, migration, admin panels, and template"
argument-hint: "Describe the new page type and its fields"
agent: "agent"
---

Create a new Wagtail page type for this project following existing conventions.

## What to build

$input

## Steps

1. **Identify the right app** — look at existing apps (`articles/`, `publications/`, `events/`, `people/`, etc.) and place the new page in the most relevant one, or `core/` if it's truly global.

2. **Create the model** in the app's `models.py`:
   - Inherit from the appropriate mixins from `core/models.py` (`BasicPageAbstract`, `ContentPage`, `FeatureablePageAbstract`, `ShareablePageAbstract`, `SearchablePageAbstract`, `ThemeablePageAbstract`) — only include what's needed
   - Define all new fields
   - Compose `body` StreamField from `BasicPageAbstract.body_default_blocks` + any extra blocks
   - Add `content_panels`, `promote_panels`, `settings_panels` following the `MultiFieldPanel` grouping pattern
   - Set `parent_page_types`, `subpage_types`, and `template` in the class body (not Meta)

3. **Generate the migration**: run `python manage.py makemigrations <app>` and verify the output.

4. **Register in wagtail_hooks.py** — add a `ModelViewSet` if admin list management is needed.

5. **Create the template** at `templates/<app>/<snake_case_name>.html`:
   - Extend `base.html`
   - Use `{% load static wagtailuserbar %}` at the top
   - Include `{% wagtailuserbar %}` in the layout
   - Render `StreamField` body with `{{ page.body }}`

6. **Write at least one test** in the app's `tests.py` verifying the page can be created and served.

## Checklist before finishing
- [ ] Migration file generated and reviewed
- [ ] `parent_page_types` set correctly
- [ ] Template file created
- [ ] Admin panels defined (content / promote / settings)
- [ ] At least one test added
