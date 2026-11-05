import csv
from collections import defaultdict
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from core.models import ContentPage
from research.models import ProjectPage, ThemePage, ThemeProgram, TopicPage

# Program backfill (docs/redesign/program-backfill-plan.md): give every live
# content page a program tag so the theme/program router pages can surface it
# (routers scope by `projects__in` — core/faceted_listing.py). Two inputs:
#   --rules  CSV of bulk rules (legacy_program -> program, topic -> program)
#   --pages  CSV of per-page assignments (the classified untagged tail)
# Only pages with no current-IA program are touched, and tags are only ever
# ADDED. Dry-run by default: writes a human-readable report (markdown) plus a
# full per-page preview CSV for client validation. --apply writes the
# `projects` through table directly (ParentalManyToManyField .add() does not
# persist) and records a reversal CSV.

# Inputs ship with the code (they run on staging/prod); outputs are local
# working documents — docs/redesign/ is untracked, so create it on demand.
DATA = Path('research/data')
DOCS = Path('docs/redesign')


class Command(BaseCommand):
    help = (
        'Backfill ContentPage.projects from mapping rules so all live content '
        'surfaces on the program/theme router pages. Dry-run by default.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--rules', default=str(DATA / 'program-backfill-rules.csv'))
        parser.add_argument('--pages', default=None,
                            help='Optional per-page CSV: page_id,program_slug,confidence')
        parser.add_argument('--report', default=str(DOCS / 'program-backfill-report.md'))
        parser.add_argument('--preview-csv', default=str(DOCS / 'program-backfill-preview.csv'))
        parser.add_argument('--reversal-csv', default=str(DOCS / 'program-backfill-reversal.csv'))
        parser.add_argument('--apply', action='store_true', help='Execute writes (default: dry-run).')

    def handle(self, *args, **options):
        DOCS.mkdir(parents=True, exist_ok=True)
        programs = {}
        for edge in ThemeProgram.objects.select_related('program', 'theme'):
            programs[edge.program.slug] = edge.program
        mapped_ids = {p.pk for p in programs.values()}

        rules = self.load_rules(options['rules'], programs)
        page_rows, unclear_ids = ([], [])
        if options['pages']:
            page_rows, unclear_ids = self.load_pages(options['pages'], programs)
            self.write_unclear(unclear_ids)

        # ProjectPage/ThemePage/TopicPage are ContentPage subclasses, but they
        # are taxonomy pages, not content — never tag them into a program.
        taxonomy_pks = (list(ProjectPage.objects.values_list('pk', flat=True))
                        + list(ThemePage.objects.values_list('pk', flat=True))
                        + list(TopicPage.objects.values_list('pk', flat=True)))
        live = ContentPage.objects.live().exclude(pk__in=taxonomy_pks)
        covered = set(live.filter(projects__id__in=mapped_ids).values_list('pk', flat=True))

        # Events were only ever program-tagged deliberately (9% historically —
        # dialogue series etc.), so the backfill must not blanket-attach them:
        # legacy_program rules still carry those deliberate tags to successors,
        # but topic rules and the classified pages skip events entirely.
        from events.models import EventPage
        event_pks = set(EventPage.objects.values_list('pk', flat=True))

        # additions[page_id] = {program_pk: set(source labels)}
        additions = defaultdict(lambda: defaultdict(set))
        rule_counts = []
        for rule in rules:
            if rule['kind'] == 'legacy_program':
                qs = live.filter(projects__id=rule['source_id'])
            else:
                qs = live.filter(topics__id=rule['source_id'])
            ids = set(qs.values_list('pk', flat=True)) - covered
            if rule['kind'] != 'legacy_program':
                ids -= event_pks
            label = f"{rule['kind']}:{rule['source_title']}"
            for pk in ids:
                additions[pk][rule['program'].pk].add(label)
            rule_counts.append((rule, len(ids)))

        page_count = 0
        for pk, program, confidence in page_rows:
            if pk in covered or pk in event_pks:
                continue
            additions[pk][program.pk].add(f'classified:{confidence}')
            page_count += 1

        total_pages = live.distinct().count()
        after = len(covered) + len(additions)
        gains = defaultdict(int)
        for targets in additions.values():
            for ppk in targets:
                gains[ppk] += 1

        self.write_preview(options['preview_csv'], additions, programs)
        self.write_report(options['report'], rules=rule_counts, programs=programs,
                          gains=gains, additions=additions, covered=len(covered),
                          total=total_pages, after=after, page_count=page_count,
                          mapped_ids=mapped_ids, live=live, apply=options['apply'],
                          event_pks=event_pks)

        if not options['apply']:
            self.stdout.write(f"DRY RUN — {len(additions)} pages would gain a program "
                              f"(coverage {len(covered)}/{total_pages} -> {after}/{total_pages}).")
            self.stdout.write(f"Report: {options['report']}  Preview: {options['preview_csv']}")
            return

        through = ContentPage.projects.through
        existing = set(through.objects.filter(
            contentpage_id__in=list(additions)).values_list('contentpage_id', 'projectpage_id'))
        to_create, reversal = [], []
        for pk, targets in additions.items():
            for ppk in targets:
                if (pk, ppk) not in existing:
                    to_create.append(through(contentpage_id=pk, projectpage_id=ppk))
                    reversal.append((pk, ppk))
        through.objects.bulk_create(to_create, ignore_conflicts=True, batch_size=1000)
        with open(options['reversal_csv'], 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['contentpage_id', 'projectpage_id'])
            w.writerows(reversal)
        self.stdout.write(f'APPLIED — {len(to_create)} links written. '
                          f"Reversal CSV: {options['reversal_csv']}")
        self.stdout.write('Run `manage.py update_index` next.')

    def load_rules(self, path, programs):
        rules = []
        with open(path, newline='') as f:
            for row in csv.DictReader(f):
                slug = row['target_program_slug'].strip()
                if slug not in programs:
                    raise CommandError(f'Unknown target program slug: {slug!r} '
                                       f'(rule {row["kind"]}:{row["source_title"]})')
                kind, source_id = row['kind'].strip(), int(row['source_id'])
                model = ProjectPage if kind == 'legacy_program' else TopicPage
                if not model.objects.filter(pk=source_id).exists():
                    raise CommandError(f'{kind} id {source_id} not found '
                                       f'({row["source_title"]})')
                rules.append({'kind': kind, 'source_id': source_id,
                              'source_title': row['source_title'],
                              'program': programs[slug], 'note': row.get('note', '')})
        return rules

    def load_pages(self, path, programs):
        rows, unclear = [], []
        with open(path, newline='') as f:
            for row in csv.DictReader(f):
                slug = row['program_slug'].strip()
                if slug == 'unclear':
                    unclear.append(int(row['page_id']))
                    continue
                if slug not in programs:
                    raise CommandError(f'Unknown program slug in pages CSV: {slug!r}')
                rows.append((int(row['page_id']), programs[slug],
                             row.get('confidence', '').strip() or 'n/a'))
        return rows, unclear

    def write_unclear(self, ids):
        # Pages the classification pass could not place (site chrome, corporate
        # announcements) — listed for an editorial call, never guessed. Events
        # drop out: they stay untagged by design, not by uncertainty.
        from events.models import EventPage
        ids = set(ids) - set(EventPage.objects.values_list('pk', flat=True))
        meta = ContentPage.objects.filter(pk__in=ids).values_list(
            'pk', 'content_type__model', 'publishing_date__year', 'title', 'url_path')
        with open(DOCS / 'program-backfill-unclear.csv', 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['page_id', 'type', 'year', 'title', 'url'])
            for pk, ct, year, title, url in sorted(meta):
                w.writerow([pk, ct.replace('page', ''), year or '', title,
                            url.replace('/home', '', 1)])

    def write_preview(self, path, additions, programs):
        slug_by_pk = {p.pk: slug for slug, p in programs.items()}
        meta = {pk: (title, url, year, ct) for pk, title, url, year, ct in
                ContentPage.objects.filter(pk__in=list(additions)).values_list(
                    'pk', 'title', 'url_path', 'publishing_date__year',
                    'content_type__model')}
        with open(path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['page_id', 'type', 'year', 'title', 'url',
                        'programs_added', 'because'])
            for pk in sorted(additions):
                title, url, year, ct = meta.get(pk, ('?', '?', '', '?'))
                targets = additions[pk]
                w.writerow([pk, ct.replace('page', ''), year or '', title,
                            url.replace('/home', '', 1),
                            ' + '.join(sorted(slug_by_pk[ppk] for ppk in targets)),
                            ' | '.join(sorted(set().union(*targets.values())))])

    def write_report(self, path, *, rules, programs, gains, additions, covered,
                     total, after, page_count, mapped_ids, live, apply,
                     event_pks=frozenset()):
        slug_by_pk = {p.pk: slug for slug, p in programs.items()}
        title_by_pk = {p.pk: p.title for p in programs.values()}
        remaining_qs = (live.exclude(pk__in=list(additions))
                        .exclude(projects__id__in=mapped_ids))
        events_skipped = remaining_qs.filter(pk__in=event_pks).distinct().count()
        remaining = remaining_qs.exclude(pk__in=event_pks).distinct().count()
        lines = [
            '# Program backfill — ' + ('APPLIED run' if apply else 'dry-run report'),
            '',
            'What this shows: every live content page that gains a program tag,',
            'so it becomes findable on the redesigned theme/program pages.',
            'Full per-page detail: [program-backfill-preview.csv](program-backfill-preview.csv).',
            '',
            f'- Live content pages: **{total}**',
            f'- Already carry a current program: **{covered}**',
            f'- Gain a program in this run: **{len(additions)}** '
            f'(of which {page_count} via per-page classification)',
            f'- Coverage after: **{after} / {total}**'
            f' ({after * 100 // max(total, 1)}%)',
            f'- Still without a program after: **{remaining}** — see '
            '[program-backfill-unclear.csv](program-backfill-unclear.csv) '
            '(mostly institutional announcements; needs an editorial call)',
            f'- Events left untagged by design: **{events_skipped}** — events '
            'were only ever program-tagged deliberately, so only legacy-program '
            'retags apply to them',
            '',
            '## Pages gained per program',
            '',
            '| Program | Pages gained |',
            '| --- | ---: |',
        ]
        for ppk, n in sorted(gains.items(), key=lambda kv: -kv[1]):
            lines.append(f'| {title_by_pk[ppk]} | {n} |')
        lines += ['', '## Mapping rules applied', '',
                  '| Rule | Target program | Pages | Rationale |',
                  '| --- | --- | ---: | --- |']
        for rule, n in rules:
            src = f"{'Legacy program' if rule['kind'] == 'legacy_program' else 'Topic'}: "
            lines.append(f"| {src}{rule['source_title']} | {rule['program'].title} "
                         f"| {n} | {rule['note']} |")
        lines += ['', 'A page that matches several rules gets every matching program '
                  '(multi-tagging is valid; listings de-duplicate).', '']
        Path(path).write_text('\n'.join(lines))
