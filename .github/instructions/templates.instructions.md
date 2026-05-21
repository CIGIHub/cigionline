---
description: "Use when creating or modifying Django/Wagtail templates, includes, stream block templates, or email templates. Covers template organization, inheritance, and template tag usage."
applyTo: "templates/**"
---

# Template Conventions

## Template Engine
Django templates (not Jinja2). Common template tag loads:
```django
{% load cache static wagtailuserbar webpack_loader %}
```

## Directory Structure
```
templates/
  base.html                     # Root layout — meta, GTM, header/footer, block definitions
  <app>/                        # App-specific page templates (e.g. articles/, events/)
  includes/
    top_bar.html
    footer.html
    heroes/                     # Hero variants per page type (hero_event.html, etc.)
    features/                   # Feature card variants
  streams/                      # One template per StreamField block (accordion_block.html, etc.)
  events/
    emails/                     # Email wrappers and merge-var snippets
    includes/                   # Shared partials (_field.html for registration fields)
    admin/                      # Wagtail admin custom views
```

## Inheritance Pattern
App templates extend `base.html` and override named blocks:
```django
{% extends "base.html" %}
{% block title %}{{ self.title }}{% endblock %}
{% block content %}
  ...
{% endblock %}
```

## Webpack Bundles
Include JS/CSS bundles using the webpack loader tag:
```django
{% render_bundle 'cigionline' 'css' %}
{% render_bundle 'cigionline' 'js' attrs='defer' %}
```

## Wagtail-Specific Tags
```django
{% wagtailuserbar %}                         {# floating edit bar for logged-in editors #}
{{ page.body }}                              {# renders StreamField #}
{% include_block block %}                    {# renders a single StreamField block #}
{% image self.image_hero width-1200 %}       {# Wagtail image tag with rendition spec #}
```

## Stream Block Templates
Each block in `streams/blocks.py` maps to a template in `templates/streams/`. Block templates receive the `value` context variable:
```django
{# templates/streams/accordion_block.html #}
<div class="accordion">
  <h3>{{ value.title }}</h3>
  <div>{{ value.text }}</div>
</div>
```

## Email Templates
Email templates live in `templates/events/emails/`. They are rendered to `(html, text)` tuples by `events/email_rendering.py`. CSS must be inlineable — avoid external stylesheets; use inline `style=""` attributes or let Premailer handle it.
