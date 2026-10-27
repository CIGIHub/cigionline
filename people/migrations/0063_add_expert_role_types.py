# Expert role types + backfill (BugHerd #359, approved by Evan 2026-09-02).
#
# The /experts/ Type facet must offer Research Directors / Distinguished
# Fellows / Senior Fellows / Fellows (Juode), but no PersonType carried those
# roles — they lived only in the free-text `position`. This migration seeds the
# four types (explicit ids, like the DPH pair in 0056) and backfills every
# Expert-typed person from their position text, most specific match first.
# PersonType is migration-managed by design (people.models.PersonType), so a
# data migration is the sanctioned insert path.
import re

from django.db import migrations

ROLE_TYPES = [
    (19, 'Research Director'),
    (20, 'Distinguished Fellow'),
    (21, 'Senior Fellow'),
    (22, 'Fellow'),
]
EXPERT_TYPE_ID = 4


def _role_for(position):
    """First-match role id for a position string (most specific first)."""
    pos = position or ''
    if pos.startswith('Research Director'):
        return 19
    if 'Distinguished Fellow' in pos:
        return 20
    if 'Senior Fellow' in pos:
        return 21
    if re.search(r'\bFellow\b', pos):
        return 22
    return None


def add_role_types(apps, schema_editor):
    PersonType = apps.get_model('people', 'PersonType')
    PersonPage = apps.get_model('people', 'PersonPage')
    for type_id, name in ROLE_TYPES:
        PersonType.objects.create(id=type_id, name=name, drupal_taxonomy_id=None)
    # Explicit-id inserts don't advance the sequence; realign it so a future
    # ORM insert can't collide.
    schema_editor.execute(
        "SELECT setval(pg_get_serial_sequence('people_persontype', 'id'), "
        "(SELECT MAX(id) FROM people_persontype))"
    )

    Through = PersonPage.person_types.through
    rows = []
    for person in PersonPage.objects.filter(person_types__id=EXPERT_TYPE_ID).distinct():
        role_id = _role_for(person.position)
        if role_id:
            rows.append(Through(personpage_id=person.pk, persontype_id=role_id))
    Through.objects.bulk_create(rows, ignore_conflicts=True)


def remove_role_types(apps, schema_editor):
    PersonType = apps.get_model('people', 'PersonType')
    PersonPage = apps.get_model('people', 'PersonPage')
    ids = [type_id for type_id, _ in ROLE_TYPES]
    PersonPage.person_types.through.objects.filter(persontype_id__in=ids).delete()
    PersonType.objects.filter(id__in=ids).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0062_alter_personlistpage_body'),
    ]

    operations = [
        migrations.RunPython(add_role_types, remove_role_types),
    ]
