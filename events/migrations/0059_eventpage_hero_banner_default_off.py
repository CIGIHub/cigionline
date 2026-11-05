# Data migration for the events hero-banner default flip: the banner becomes
# opt-in. Events whose authored image_hero is actually hero-sized (>=1920px
# wide) keep it on; everything else (no image, or a small poster that would
# upscale badly) is switched off. Irreversible by design (the old all-on state
# carried no per-event intent - it was just the old default).

from django.db import migrations


def set_banner_by_image_size(apps, schema_editor):
    EventPage = apps.get_model('events', 'EventPage')
    suitable = EventPage.objects.filter(image_hero__width__gte=1920)
    EventPage.objects.exclude(pk__in=suitable).update(show_hero_banner=False)
    suitable.update(show_hero_banner=True)


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0058_alter_eventpage_show_hero_banner'),
    ]

    operations = [
        migrations.RunPython(set_banner_by_image_size, migrations.RunPython.noop),
    ]
