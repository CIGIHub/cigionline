from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import ContentPage
from research.models import ProjectPage, TopicPage

# PROVISIONAL GCG topic->program mapping — a deliberately loose fit, used only to
# populate the GCG theme so the dynamic modules (Program Spotlight, etc.) can be
# built and tested against real content. This is NOT a curated editorial mapping.
#
# Forward (--apply): publish each net-new GCG program shell, then add it to the
# `projects` M2M of every live content page tagged with the mapped topic (this
# feeds `program.content_pages`, which the Spotlight renders).
# Reverse (--revert --apply): unlink the programs from that content and unpublish
# them again. Idempotent in both directions. Dry-run unless --apply is passed.
MAPPING = [
    ('Multilateral Institutions', 'Multilateral and Institutional Reform'),
    ('Geopolitics', 'India and China in a Multipolar World'),
    ('Trade', 'Canada-US Relations in the Second Century'),
]


class Command(BaseCommand):
    help = (
        'Provisionally populate the GCG programs with content via a loose '
        'topic->program mapping, for building/testing the dynamic modules. '
        'Dry-run by default; --apply to write, --revert --apply to undo.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Execute writes (default: dry-run).')
        parser.add_argument('--revert', action='store_true', help='Undo: unlink content + unpublish the programs.')

    def handle(self, *args, **options):
        write = options['apply']
        revert = options['revert']
        mode = ('REVERT ' if revert else '') + ('APPLY' if write else 'DRY RUN')
        self.stdout.write(f'== GCG program content backfill ({mode}) ==')

        for topic_title, program_title in MAPPING:
            topic = TopicPage.objects.filter(title=topic_title).first()
            program = ProjectPage.objects.filter(title=program_title).first()
            if topic is None or program is None:
                self.stderr.write(f'  MISSING — topic "{topic_title}" or program "{program_title}" not found; skipped')
                continue

            # `projects` is a ParentalManyToManyField — .add() only mutates the
            # in-memory cluster, so write the through table directly instead.
            through = ContentPage.projects.through

            if revert:
                # net-new programs had no content before this backfill, so every
                # link is ours — remove them all and unpublish.
                links = through.objects.filter(projectpage_id=program.pk)
                self.stdout.write(
                    f'{topic_title} -> {program_title}: unlink {links.count()} pages; '
                    f'unpublish program (live={program.live})'
                )
                if write:
                    links.delete()
                    if program.live:
                        program.unpublish()
                continue

            content_ids = list(
                ContentPage.objects.live().filter(topics=topic).values_list('pk', flat=True).distinct()
            )
            already = set(
                through.objects.filter(projectpage_id=program.pk, contentpage_id__in=content_ids)
                .values_list('contentpage_id', flat=True)
            )
            to_link = [cid for cid in content_ids if cid not in already]
            self.stdout.write(
                f'{topic_title} -> {program_title}: {len(content_ids)} tagged, '
                f'{len(to_link)} to link; publish program (live={program.live})'
            )
            if write:
                if not program.live:
                    # shells were created without a publishing_date, which is
                    # required to publish — stamp it before publishing.
                    if not program.publishing_date:
                        program.publishing_date = timezone.now()
                    program.save_revision().publish()
                through.objects.bulk_create(
                    [through(contentpage_id=cid, projectpage_id=program.pk) for cid in to_link],
                    ignore_conflicts=True,
                    batch_size=1000,
                )

        if write:
            self.stdout.write('Done.')
        else:
            self.stdout.write('Dry run only — re-run with --apply to execute.')
