from django.apps import apps
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from research.models import ProjectPage, ThemePage, ThemeProgram, TopicPage

# Portion 1 of the dynamic-modules plan: populate the entities the modules render
# (programs, themes, topics) with PLACEHOLDER images + subtitles so the modules
# can be built/QA'd against real-looking data. Editorial replaces this later.
# Idempotent: fills only empty fields. Reversible: --revert clears exactly the
# placeholder values this command set. See docs/redesign/dynamic-modules-data-and-controls.md.

PLACEHOLDER_SUBTITLE = 'Placeholder subtitle for QA — replace with editorial copy.'

# (model resolver, queryset fn, image fields, set subtitle?)
#   programs need image_feature (panel/accent-media) + image_hero; themes/topics
#   need image_hero + image_banner for grid/hero modules.


class Command(BaseCommand):
    help = (
        'Seed placeholder images + subtitles on programs/themes/topics for module QA. '
        'Dry-run by default; --apply to write, --revert --apply to undo.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Execute writes (default: dry-run).')
        parser.add_argument('--revert', action='store_true', help='Clear the placeholder values this command set.')

    def handle(self, *args, **options):
        write = options['apply']
        revert = options['revert']
        mode = ('REVERT ' if revert else '') + ('APPLY' if write else 'DRY RUN')
        self.stdout.write(f'== Module placeholder data ({mode}) ==')

        Image = apps.get_model(getattr(settings, 'WAGTAILIMAGES_IMAGE_MODEL', 'wagtailimages.Image'))
        # Only images whose SOURCE file exists in storage. On a DB-only restore
        # (no local media) the rest have rows but no files, so their <img>/
        # renditions 404 in the browser; locally that's just the few uploaded
        # images. On a full media setup this is effectively every image.
        pool = [
            pk for pk, f in Image.objects.order_by('pk').values_list('pk', 'file')
            if f and 'logo' not in f.lower() and default_storage.exists(f)
        ]
        if not pool:
            self.stderr.write('No images with a local source file — aborting (nothing would render).')
            return
        self.stdout.write(f'placeholder image pool: {len(pool)} local images')

        # Build the work list in a STABLE order so --revert recomputes the same
        # image assignments and can match/clear them.
        prog_ids = list(ThemeProgram.objects.values_list('program', flat=True))
        groups = [
            ('program', ProjectPage.objects.filter(pk__in=prog_ids).order_by('pk'), ['image_feature', 'image_hero'], True),
            ('theme', ThemePage.objects.filter(archive=0, live=True).order_by('pk'), ['image_hero', 'image_banner'], False),
            ('topic', TopicPage.objects.filter(archive=0, live=True).order_by('pk'), ['image_hero', 'image_banner'], False),
        ]

        idx = 0
        for kind, qs, image_fields, set_subtitle in groups:
            n_imgs = n_subs = 0
            for obj in qs:
                changed = []
                for field in image_fields:
                    img_pk = pool[idx % len(pool)]
                    idx += 1
                    current = getattr(obj, f'{field}_id')
                    if revert:
                        if current == img_pk:
                            setattr(obj, f'{field}_id', None)
                            changed.append(field)
                            n_imgs += 1
                    elif current is None:
                        setattr(obj, f'{field}_id', img_pk)
                        changed.append(field)
                        n_imgs += 1
                if set_subtitle:
                    if revert:
                        if obj.feature_subtitle == PLACEHOLDER_SUBTITLE:
                            obj.feature_subtitle = ''
                            changed.append('feature_subtitle')
                            n_subs += 1
                    elif not obj.feature_subtitle:
                        obj.feature_subtitle = PLACEHOLDER_SUBTITLE
                        changed.append('feature_subtitle')
                        n_subs += 1
                if changed and write:
                    obj.save(update_fields=changed)
            verb = 'cleared' if revert else 'filled'
            self.stdout.write(f'{kind}s: {verb} {n_imgs} image fields, {n_subs} subtitles')

        if write:
            self.stdout.write('Done. (image index updates may log harmless ES connection errors)')
        else:
            self.stdout.write('Dry run only — re-run with --apply to execute.')
