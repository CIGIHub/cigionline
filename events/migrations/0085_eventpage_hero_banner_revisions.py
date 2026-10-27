# Follow-up to 0058/0059 (found under BugHerd #520): 0059 kept the banner on
# in the page table for events with a hero-sized image, but left their
# revisions alone. Those revisions predate the field, so they carry no
# show_hero_banner key and load the new False default. The editor reads the
# revision only when a page has unpublished changes (drafts, unpublished
# events): those open unticked and the next publish silently drops the
# banner. Live events without a draft open from the table, but reverting to
# or reviewing the live revision, unpublishing then editing, or copying the
# page would drop it the same way.
#
# Writes an explicit `true` into the latest and live revision of every event
# whose table value is True and whose revision lacks the key. Explicit values
# (editor choices) are never overwritten; table-False pages already agree with
# the default. Older revisions are left as history. No new revisions; no
# other field, page type or timestamp is touched.
#
# Reverse is a no-op: removing the key would reintroduce the mismatch.

from django.db import migrations


def write_banner_into_revisions(apps, schema_editor):
    EventPage = apps.get_model('events', 'EventPage')
    Revision = apps.get_model('wagtailcore', 'Revision')
    revision_ids = set()
    for ids in EventPage.objects.filter(show_hero_banner=True).values_list('latest_revision_id', 'live_revision_id'):
        revision_ids.update(pk for pk in ids if pk)
    revisions = Revision.objects.filter(pk__in=revision_ids).exclude(content__has_key='show_hero_banner')
    for revision in revisions.iterator():
        revision.content['show_hero_banner'] = True
        revision.save(update_fields=['content'])


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0084_alter_eventlistpage_body'),
        ('wagtailcore', '0096_referenceindex_referenceindex_source_object_and_more'),
    ]

    operations = [
        migrations.RunPython(write_banner_into_revisions, migrations.RunPython.noop),
    ]
