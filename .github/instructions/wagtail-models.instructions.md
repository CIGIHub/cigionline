---
description: "Use when creating or modifying Wagtail page models, migrations, model mixins, StreamFields, or admin panels. Covers page model conventions, panel patterns, and migration requirements."
applyTo: "*/models.py, */migrations/*.py"
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
Always use `use_json_field=True`. Compose body blocks from `BasicPageAbstract` class-level block lists:
```python
body = StreamField(
    BasicPageAbstract.body_default_blocks + [
        BasicPageAbstract.body_accordion_block,
        BasicPageAbstract.body_chart_block,
    ],
    blank=True,
    use_json_field=True,
)
```

## Admin Panels Pattern
Always group with `MultiFieldPanel`. Follow the content/promote/settings split:
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
Always define `parent_page_types`, `subpage_types`, and `template`:
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
- Never edit existing migrations — always generate new ones
- Use `AlterField` for changes to existing fields (e.g. adding choices to a CharField)

## Wagtail Hooks
- Register ModelViewSets, snippets, and admin customizations in each app's `wagtail_hooks.py`
- Use `@hooks.register('insert_global_admin_js')` for injecting admin JavaScript
- Custom admin forms (e.g. password hashing) go in `forms_admin.py`, not `models.py`
