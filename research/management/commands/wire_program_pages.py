from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from research.models import ProjectPage, ThemePage, ThemeProgram


PROGRAMS = [
    ('Global Cooperation and Governance', [
        (('India and China in a Multipolar World',), 0),
        (('Multilateral and Institutional Reform',), 1),
        (('Canada-US Relations in the Second Century',), 2),
    ]),
]


def get_one(model, titles):
    variants = set(titles)
    variants.update(title.replace('’', "'") for title in titles)
    return list(model.objects.filter(title__in=variants).order_by('pk')[:2])


class Command(BaseCommand):
    help = 'Wire existing project pages into their theme menus without creating pages.'

    def handle(self, *args, **options):
        rows = []
        errors = []

        for theme_title, programs in PROGRAMS:
            themes = get_one(ThemePage, (theme_title,))
            if len(themes) != 1:
                errors.append(f'{theme_title!r}: expected one ThemePage, found {len(themes)}')
                continue
            for program_titles, sort_order in programs:
                pages = get_one(ProjectPage, program_titles)
                if len(pages) != 1:
                    errors.append(
                        f'{program_titles[0]!r}: expected one ProjectPage, found {len(pages)}'
                    )
                    continue
                rows.append((themes[0], pages[0], sort_order))

        if errors:
            raise CommandError('Program wiring preflight failed:\n- ' + '\n- '.join(errors))

        with transaction.atomic():
            for theme, program, sort_order in rows:
                edge, created = ThemeProgram.objects.get_or_create(
                    theme=theme,
                    program=program,
                    defaults={'sort_order': sort_order, 'label': ''},
                )
                self.stdout.write(
                    f'{"wired" if created else "ok"}: {theme.title} -> {program.title}'
                )

