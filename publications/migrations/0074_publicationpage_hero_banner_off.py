# Data migration for the publications hero-banner default flip (Tim, BugHerd
# #520): the banner becomes opt-in, and every existing publication is switched
# off — the old all-on state carried no per-page intent (0047 back-filled the
# old default; no publication was ever toggled on deliberately and left on).
#
# The editor loads a page from its latest REVISION, not the page table, and
# publish/revert apply revision content — so revisions must agree with the
# table or the next publish silently flips the banner back. Revisions without
# the key already load the new False default; only explicit `true`s are
# rewritten. That covers every PublicationPage revision, not just latest/live:
# the older trues sit mostly on pages editors already turned off by hand
# (23725, 23832), and reverting one of them would bring the banner back.
# No new revisions; no other field, page type or timestamp is touched.
#
# Irreversible by design: restoring the old values needs the pre-deploy
# snapshot of page/revision ids that were on.

from django.db import migrations


def hero_banner_off(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    PublicationPage = apps.get_model('publications', 'PublicationPage')
    Revision = apps.get_model('wagtailcore', 'Revision')
    PublicationPage.objects.filter(show_hero_banner=True).update(show_hero_banner=False)
    revisions = Revision.objects.filter(
        content_type__in=ContentType.objects.filter(app_label='publications', model='publicationpage'),
        content__show_hero_banner=True,
    )
    for revision in revisions.iterator():
        revision.content['show_hero_banner'] = False
        revision.save(update_fields=['content'])


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('publications', '0073_alter_publicationpage_show_hero_banner'),
        ('wagtailcore', '0096_referenceindex_referenceindex_source_object_and_more'),
    ]

    operations = [
        # Reverse is a no-op: see the header — use the pre-deploy snapshot.
        migrations.RunPython(hero_banner_off, migrations.RunPython.noop),
    ]
