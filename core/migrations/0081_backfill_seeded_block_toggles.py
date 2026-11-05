"""Backfill BooleanBlock keys the seed scripts omitted (BugHerd #18).

Pages seeded programmatically stored their StreamField bodies verbatim from the
seed dicts, so BooleanBlock fields left out of those dicts are ABSENT from the
stored JSON. At render time a StructValue falls back to the block default (so the
frontend shows pagination, dates, etc.), but the Wagtail editor reads the raw
stored value and renders the checkbox UNCHECKED — the mismatch QA reported.

This fills the missing keys with their block defaults on existing content so the
editor reflects reality. It only ADDS absent keys (never overwrites an authored
value), and patches both the live page bodies and the latest revisions the editor
loads. New blocks added in the editor already initialise from the block default,
so this is purely a one-time fix for seeded data.
"""
import json

from django.db import migrations


# type -> {key: default} for keys to add when absent on the block value.
TOP_LEVEL_DEFAULTS = {
    'experts_carousel': {'show_pagination': True},
    'resource_bento': {'show_header': True, 'show_date': True, 'show_author': True},
}
# type -> {nested StructBlock field: {key: default}}
NESTED_DEFAULTS = {
    'experts_carousel': {'card_slots': {'show_read_bio': False}},
}
# Page models whose body uses body_default_blocks (the blocks above live there).
AFFECTED_MODELS = [
    ('articles', 'ArticlePage'),
    ('core', 'BasicPage'),
    ('home', 'HomePage'),
    ('multimedia', 'MultimediaSeriesPage'),
    ('research', 'ProjectPage'),
]


def _load(raw):
    """A StreamField body as a list of blocks, or None if it can't be parsed."""
    if raw in (None, ''):
        return None
    if isinstance(raw, list):
        return raw
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return None


def _patch_stream(stream):
    """Add any absent BooleanBlock keys to matching top-level blocks. Returns
    True when the stream was modified."""
    if not isinstance(stream, list):
        return False
    changed = False
    for block in stream:
        if not isinstance(block, dict):
            continue
        btype = block.get('type')
        value = block.get('value')
        if not isinstance(value, dict):
            continue
        for key, default in TOP_LEVEL_DEFAULTS.get(btype, {}).items():
            if key not in value:
                value[key] = default
                changed = True
        for field, keys in NESTED_DEFAULTS.get(btype, {}).items():
            nested = value.get(field)
            if isinstance(nested, dict):
                for key, default in keys.items():
                    if key not in nested:
                        nested[key] = default
                        changed = True
    return changed


def backfill(apps, schema_editor):
    connection = schema_editor.connection
    quote = connection.ops.quote_name

    # 1) Live page bodies — read/write the raw JSON text column directly so no
    #    block definitions are needed in the historical migration state.
    with connection.cursor() as cursor:
        for app_label, model_name in AFFECTED_MODELS:
            model = apps.get_model(app_label, model_name)
            table = quote(model._meta.db_table)
            # Page subclasses use multi-table inheritance — the PK column is
            # page_ptr_id, not id.
            pk_col = quote(model._meta.pk.column)
            cursor.execute('SELECT %s, body FROM %s' % (pk_col, table))
            for pk, body in cursor.fetchall():
                data = _load(body)
                if _patch_stream(data):
                    cursor.execute(
                        'UPDATE %s SET body = %%s WHERE %s = %%s' % (table, pk_col),
                        [json.dumps(data), pk],
                    )

    # 2) Latest revisions the editor loads. Revision.content is a dict; its
    #    'body' entry holds the stream as a JSON string.
    Revision = apps.get_model('wagtailcore', 'Revision')
    for rev in Revision.objects.all().iterator():
        content = rev.content
        if not isinstance(content, dict) or 'body' not in content:
            continue
        data = _load(content['body'])
        if _patch_stream(data):
            content['body'] = json.dumps(data)
            rev.content = content
            rev.save(update_fields=['content'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0080_alter_footersettings_address'),
        ('articles', '0119_alter_articlepage_body'),
        ('home', '0029_alter_homepage_body'),
        ('multimedia', '0065_alter_multimediaseriespage_body'),
        ('research', '0085_alter_projectpage_body'),
        ('wagtailcore', '0096_referenceindex_referenceindex_source_object_and_more'),
    ]

    operations = [
        # Data-only, additive; reverse is a no-op (defaults are re-derived on render).
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
