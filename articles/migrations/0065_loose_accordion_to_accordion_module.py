import json
import uuid

from django.db import migrations


def _new_id():
    return uuid.uuid4().hex


def loose_accordion_to_module(apps, schema_editor):
    """Replace runs of consecutive loose `accordion` blocks with a single
    `accordion_module` whose `items` are the original accordions ({title, text}).

    The legacy AccordionBlock also had a `columns` field; the redesign drops it,
    so it is not carried over.
    """
    ArticlePage = apps.get_model('articles', 'ArticlePage')

    for page in ArticlePage.objects.all().iterator():
        raw = page.body.raw_data
        if not any(b.get('type') == 'accordion' for b in raw):
            continue

        new_raw = []
        run = []

        def flush_run():
            if not run:
                return
            items = [
                {
                    'type': 'item',
                    'value': {
                        'title': b['value'].get('title', ''),
                        'text': b['value'].get('text', ''),
                    },
                    'id': _new_id(),
                }
                for b in run
            ]
            new_raw.append({
                'type': 'accordion_module',
                'value': {
                    'heading': '',
                    'intro_text': '',
                    'buttons': [],
                    'items': items,
                },
                'id': _new_id(),
            })
            run.clear()

        for b in raw:
            if b.get('type') == 'accordion':
                run.append(b)
            else:
                flush_run()
                new_raw.append(b)
        flush_run()

        page.body = json.dumps(new_raw)
        page.save(update_fields=['body'])


def module_to_loose_accordion(apps, schema_editor):
    """Reverse: expand `accordion_module` blocks that carry no heading/intro/buttons
    back into loose `accordion` blocks (the shape this migration produced).
    Modules with intro content are left intact — they did not originate here.
    """
    ArticlePage = apps.get_model('articles', 'ArticlePage')

    for page in ArticlePage.objects.all().iterator():
        raw = page.body.raw_data
        if not any(b.get('type') == 'accordion_module' for b in raw):
            continue

        new_raw = []
        for b in raw:
            v = b.get('value', {})
            is_bare = (
                b.get('type') == 'accordion_module'
                and not v.get('heading')
                and not v.get('intro_text')
                and not v.get('buttons')
            )
            if not is_bare:
                new_raw.append(b)
                continue
            for item in v.get('items', []):
                iv = item.get('value', {})
                new_raw.append({
                    'type': 'accordion',
                    'value': {
                        'title': iv.get('title', ''),
                        'text': iv.get('text', ''),
                        'columns': '',
                    },
                    'id': _new_id(),
                })

        page.body = json.dumps(new_raw)
        page.save(update_fields=['body'])


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0064_alter_articlepage_body'),
    ]

    operations = [
        migrations.RunPython(loose_accordion_to_module, module_to_loose_accordion),
    ]
