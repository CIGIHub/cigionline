# Generated by Django 3.1.7 on 2021-03-02 18:42

from django.db import migrations


def populate_person_types(apps, schema_editor):
    DEFAULT_TYPES = [
        (20, 'Board Member'),
        (933, 'CIGI Chair'),
        (943, 'Commission'),
        (18, 'Expert'),
        (850, 'External profile'),
        (627, 'G20 Expert'),
        (19, 'Management Team'),
        (897, 'Media Contact'),
        (751, 'Person'),
        (893, 'Program Director'),
        (894, 'Program Manager'),
        (944, 'Research Advisor'),
        (891, 'Research Associate'),
        (892, 'Research Fellow'),
        (41, 'Speaker'),
        (22, 'Staff'),
    ]
    PersonType = apps.get_model('people', 'PersonType')
    for drupal_id, person_type_name in DEFAULT_TYPES:
        person_type = PersonType(name=person_type_name, drupal_taxonomy_id=drupal_id)
        person_type.save()


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0002_auto_20210302_1216'),
    ]

    operations = [
        migrations.RunPython(populate_person_types),
    ]
