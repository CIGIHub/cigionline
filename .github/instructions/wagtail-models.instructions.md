---
description: 'Use when creating or modifying Wagtail page models, migrations, model mixins, StreamFields, or admin panels. Covers page model conventions, panel patterns, and migration requirements.'
applyTo: '*/models.py, */migrations/*.py'
---

# Wagtail Page Model Conventions

## Inheritance Pattern

Page models inherit from multiple abstract mixins. Compose from:

- `BasicPageAbstract` — `subtitle`, `body` StreamField (~25 blocks), hero fields, word count/read time
- `ContentPage` — `publishing_date`, M2M `topics`, `countries`, `projects`; base for articles/publications/events
- `FeatureablePageAbstract` — feature image, title, subtitle for homepage cards
- `SearchablePageAbstract` — search terms, result description, exclusion flag
- `ShareablePageAbstract` — social title, description, image (OG meta)
- `ThemeablePageAbstract` — theme FK, `get_theme_dir()`

Example:

```python
class ArticlePage(BasicPageAbstract, ContentPage, FeatureablePageAbstract, ShareablePageAbstract, ...):
    ...
```

## StreamField Pattern

Use the inherited `BasicPageAbstract.body` unless the page type needs a deliberately different block set. When overriding it, keep `use_json_field=True` and compose from the existing class-level lists, including shared module blocks where appropriate:

```python
body = StreamField(
    BasicPageAbstract.body_default_blocks
    + BasicPageAbstract.body_module_blocks
    + [
        BasicPageAbstract.body_accordion_block,
    ],
    blank=True,
    use_json_field=True,
)
```

## Admin Panels Pattern

Follow the surrounding model's content/promote/settings split and reuse shared panels. Use `MultiFieldPanel` where fields form a meaningful group:

```python
content_panels = [
    BasicPageAbstract.title_panel,          # MultiFieldPanel with title+subtitle
    MultiFieldPanel([...], heading='Body'), # Main content
    ContentPage.authors_panel,              # from mixin
    MultiFieldPanel([...], heading='Images'),
]
promote_panels = Page.promote_panels + [
    FeatureablePageAbstract.feature_panel,
    ShareablePageAbstract.social_panel,
    SearchablePageAbstract.search_panel,
]
settings_panels = ContentPage.settings_panels + [
    ThemeablePageAbstract.theme_panel,
]
```

## Meta Class

Define `parent_page_types`, `subpage_types`, and `template` when the page type needs to constrain or override them:

```python
class Meta:
    verbose_name = 'Article'
    verbose_name_plural = 'Articles'

parent_page_types = ['articles.ArticleListPage']
subpage_types = []
template = 'articles/article_page.html'
```

## Migrations

- Every new model field requires a migration: `python manage.py makemigrations`
- After adding a field and writing the migration, also update the template
- Read `docs/master-to-redesign-porting.md` before porting or reconciling migrations
- Never rewrite a migration already applied to production; production migration identity and history are authoritative
- If a redesign migration collides with a production migration name, preserve the production migration and recreate the redesign operations under a new name with corrected dependencies
- Never resolve migration conflicts by editing `django_migrations` or using `migrate --fake`
- Use `AlterField` for changes to existing fields (e.g. adding choices to a CharField)
- Verify with `python manage.py makemigrations --check --dry-run` and test the migration path against a production-clone database

## Wagtail Hooks

- Register ModelViewSets, snippets, and admin customizations in each app's `wagtail_hooks.py`
- Use `@hooks.register('insert_global_admin_js')` for injecting admin JavaScript
- Custom admin forms (e.g. password hashing) go in `forms_admin.py`, not `models.py`
