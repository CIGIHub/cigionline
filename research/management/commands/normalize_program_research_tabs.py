import json

from django.core.management.base import BaseCommand

from research.models import ProjectPage

# BugHerd #488 (John; Tia 9/8: "they should all be the same for each in terms
# of filtering"). Program pages' Research tabs were authored with different
# faceted-listing card types — resource (correct: the program's own content,
# filters Topic/Type/Year), publication (WRONG: the Working Paper catalogue,
# not the program's content) and expert (WRONG: people, theme filter). This
# normalises every faceted listing inside a ProjectPage's tabs to the
# program-scoped resource listing. Dry-run by default.

RESOURCE_DEFAULTS = {
    'card_type': 'resource',
    'program_source': 'auto',
    'program': None,
    'content_types': [],   # all four types; filters auto-build from them
}


class Command(BaseCommand):
    help = (
        'Normalise the faceted listings inside program (ProjectPage) tabs to the '
        'program-scoped resource card type so every program page filters the same '
        'way (BugHerd #488). Dry-run by default — pass --apply to write.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Execute writes (default: dry-run).')

    def handle(self, *args, **options):
        changed_pages = 0
        for page in ProjectPage.objects.live().order_by('path'):
            raw = list(page.body.raw_data)
            hits = []
            for block in raw:
                if block.get('type') != 'composable_tabs':
                    continue
                for tab in block['value'].get('tabs') or []:
                    tab_value = tab.get('value') or tab
                    for child in tab_value.get('content') or []:
                        if child.get('type') != 'faceted_listing':
                            continue
                        v = child['value']
                        if v.get('card_type') in ('resource', 'resource-visual') \
                                and (v.get('program_source') or 'auto') == 'auto':
                            continue
                        hits.append((tab_value.get('label'), v.get('card_type'), v))
            if not hits:
                continue
            changed_pages += 1
            for label, card_type, v in hits:
                self.stdout.write(f'{page.id:6d}  {page.slug:45s}  tab "{label}": {card_type} -> resource')
                v.update(RESOURCE_DEFAULTS)
            if options['apply']:
                page.body = json.dumps(raw)
                rev = page.save_revision(log_action=True)
                if page.live:
                    rev.publish()
        if not changed_pages:
            self.stdout.write('Every program tab listing is already the resource type — nothing to do.')
            return
        self.stdout.write(f'\n{changed_pages} program page(s) with non-resource tab listings.')
        if not options['apply']:
            self.stdout.write('Dry run — nothing written. Re-run with --apply.')
