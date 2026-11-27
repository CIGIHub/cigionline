import json

from django.db import migrations
from django.db.models import F, JSONField
from django.db.models.functions import Cast
from wagtail.fields import StreamField


PAGE_APPS = {
    'annual_reports', 'articles', 'careers', 'core', 'events', 'home',
    'multimedia', 'newsletters', 'people', 'portal', 'publications',
    'research', 'subscribe',
}


def add_theme_facet(value):
    changed = False
    if isinstance(value, list):
        for item in value:
            changed = add_theme_facet(item) or changed
    elif isinstance(value, dict):
        if value.get('type') == 'faceted_listing':
            config = value.get('value')
            if isinstance(config, dict) and config.get('card_type') == 'expert':
                facets = config.get('facets') or []
                if 'topic' in facets and 'theme' not in facets:
                    config['facets'] = [*facets, 'theme']
                    changed = True
        for item in value.values():
            changed = add_theme_facet(item) or changed
    return changed


def migrate_expert_theme_facets(apps, schema_editor):
    alias = schema_editor.connection.alias
    Page = apps.get_model('wagtailcore', 'Page')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Revision = apps.get_model('wagtailcore', 'Revision')
    stream_fields = {}

    for model in apps.get_models():
        if (model._meta.app_label not in PAGE_APPS
                or not issubclass(model, Page) or model._meta.proxy):
            continue
        fields = [field for field in model._meta.get_fields()
                  if isinstance(field, StreamField)]
        if not fields:
            continue
        stream_fields[(model._meta.app_label, model._meta.model_name)] = [
            field.name for field in fields
        ]
        for field in model._meta.local_fields:
            if not isinstance(field, StreamField):
                continue
            objects = model.objects.using(alias)
            candidates = objects.annotate(
                raw_stream=Cast(F(field.name), JSONField())
            ).filter(raw_stream__icontains='faceted_listing')
            for instance in candidates.iterator(chunk_size=500):
                if add_theme_facet(instance.raw_stream):
                    objects.filter(pk=instance.pk).update(**{field.name: instance.raw_stream})

    content_types = {
        ct.pk: stream_fields[(ct.app_label, ct.model)]
        for ct in ContentType.objects.using(alias).all()
        if (ct.app_label, ct.model) in stream_fields
    }
    revisions = Revision.objects.using(alias).filter(
        content_type_id__in=content_types, content__icontains='faceted_listing')
    for revision in revisions.iterator(chunk_size=500):
        changed = False
        for field_name in content_types[revision.content_type_id]:
            value = revision.content.get(field_name)
            if isinstance(value, str):
                if 'faceted_listing' not in value:
                    continue
                raw = json.loads(value)
                if add_theme_facet(raw):
                    revision.content[field_name] = json.dumps(raw)
                    changed = True
            elif isinstance(value, (list, dict)) and add_theme_facet(value):
                changed = True
        if changed:
            Revision.objects.using(alias).filter(pk=revision.pk).update(content=revision.content)


class Migration(migrations.Migration):
    dependencies = [
        ('annual_reports', '0098_alter_annualreportlistpage_body'),
        ('articles', '0160_alter_articlelandingpage_body_and_more'),
        ('careers', '0066_alter_jobpostinglistpage_body'),
        ('core', '0127_alter_basicpage_body_alter_fundingpage_body_and_more'),
        ('events', '0100_alter_eventlistpage_body'),
        ('home', '0064_alter_homepage_body'),
        ('multimedia', '0107_alter_multimedialistpage_body_and_more'),
        ('newsletters', '0061_alter_newsletterlistpage_body'),
        ('people', '0078_alter_personlistpage_body'),
        ('portal', '0045_alter_portalhomepage_body_alter_portalpage_body'),
        ('publications', '0085_alter_publicationlistpage_body_and_more'),
        ('research', '0131_alter_countrypage_body_alter_projectpage_body_and_more'),
        ('subscribe', '0064_alter_subscribepage_body'),
    ]

    operations = [migrations.RunPython(migrate_expert_theme_facets)]
