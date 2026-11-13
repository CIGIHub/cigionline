---
description: 'Use when creating or modifying Django/Wagtail templates, includes, stream block templates, or email templates. Covers template organization, inheritance, and template tag usage.'
applyTo: 'templates/**'
---

# Template Conventions

## Template Engine

Django templates (not Jinja2). Common template tag loads:

```django
{% load cache static wagtailuserbar webpack_loader %}
```

Load project tags such as `heroes`, `cards`, and `icons` only where they are used.

## Directory Structure

```
templates/
  base.html                     # Root layout — meta, GTM, header/footer, block definitions
  <app>/                        # App-specific page templates (e.g. articles/, events/)
  includes/
    top_bar.html
    footer.html
    ds_*                        # Shared design-system components
  streams/                      # One template per StreamField block (accordion_block.html, etc.)
  events/
    emails/                     # Email wrappers and merge-var snippets
    includes/                   # Event-specific partials, including guest registration
    admin/                      # Wagtail admin custom views
```

## Inheritance Pattern

App templates extend `base.html`, use the shared page hero and design-system layout, and override named blocks:

```django
{% extends "base.html" %}
{% load wagtailcore_tags heroes cards %}
{% block title %}{{ self.title }}{% endblock %}
{% block content %}
  {% page_hero self %}
  {% for section in self.body|body_sections %}
    {% if section.kind == 'module' %}
      {% include_block section.block %}
    {% else %}
      <div class="ds-surface ds-surface--light">
        <div class="ds-reading ds-reading--section ds-container">
          <div class="ds-reading__main"><div class="ds-prose">
            {% for block in section.blocks %}{% include_block block %}{% endfor %}
          </div></div>
        </div>
      </div>
    {% endif %}
  {% endfor %}
{% endblock %}
```

Follow a nearby redesigned page rather than recreating page chrome or legacy Bootstrap structures. Read `docs/redesign/README.md` before changing shared redesign architecture.

## Webpack Bundles

Include JS/CSS bundles using the webpack loader tag:

```django
{% render_bundle 'cigionline' 'css' %}
{% render_bundle 'cigionline' 'js' attrs='defer' %}
```

## Wagtail-Specific Tags

```django
{% page_hero self %}                         {# shared hero selected for the page #}
{% include_block block %}                    {# renders a single StreamField block #}
{% image self.image_hero width-1200 %}       {# Wagtail image tag with rendition spec #}
```

## Stream Block Templates

Blocks in `streams/blocks.py` generally map to templates in `templates/streams/`. Block templates receive the `value` context variable; follow the closest existing block's markup and accessibility pattern:

```django
{# templates/streams/example_block.html #}
<section class="ds-surface ds-surface--light">
  <div class="ds-container">{{ value.heading }}</div>
</section>
```

Reuse existing stream blocks and design-system components before adding another template or style variant. Shared block definitions live in `streams/blocks.py`; shared presentation belongs in the design-system CSS/JS directories.

## Email Templates

Email templates live in `templates/events/emails/`. They are rendered to `(html, text)` tuples by `events/email_rendering.py`. CSS must be inlineable — avoid external stylesheets; use inline `style=""` attributes or let Premailer handle it.
