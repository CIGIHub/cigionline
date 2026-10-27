from django.core.management.base import BaseCommand
from django.utils.text import slugify
from wagtail.models import Page

from research.models import ProjectPage, ThemePage, ThemeProgram

# The 4 net-new program pages from the IA hierarchy (2026-06-11), extracted
# from migration research/0067 — page creation needs Page.add_child, which
# historical migration models don't have. Idempotent: run after `migrate` on
# every environment (close-out.md staging sequence); re-runs are no-ops.
PROGRAMS = [
    ('Digitalization, Security and Democracy', [
        ('Freedom of Thought', 2),
    ]),
    ('Global Cooperation and Governance', [
        ('India and China in a Multipolar World', 0),
        ('Multilateral and Institutional Reform', 1),
        ('Canada-US Relations in the Second Century', 2),
    ]),
]


def get_by_title(model, title):
    qs = model.objects.filter(title=title)
    if not qs.exists():
        qs = model.objects.filter(title=title.replace('’', "'"))
    return qs.first()


class Command(BaseCommand):
    help = (
        'Create the 4 net-new program page shells (unpublished drafts) and wire '
        'their ThemeProgram rows. Idempotent; run after migrate.'
    )

    def handle(self, *args, **options):
        parent = Page.objects.filter(slug='programs').order_by('depth').first()
        if parent is None:
            self.stderr.write("'Programs' parent page not found — aborting")
            return

        for theme_title, programs in PROGRAMS:
            theme = get_by_title(ThemePage, theme_title)
            if theme is None:
                self.stderr.write(f'ThemePage not found, skipping: {theme_title}')
                continue

            for program_title, sort_order in programs:
                program = get_by_title(ProjectPage, program_title)
                if program is None:
                    program = ProjectPage(
                        title=program_title,
                        draft_title=program_title,
                        slug=slugify(program_title),
                        live=False,  # unpublished shell — editors add content then publish
                    )
                    parent.add_child(instance=program)
                    self.stdout.write(f'created shell: {program_title}')
                _, created = ThemeProgram.objects.get_or_create(
                    theme=theme,
                    program=program,
                    defaults={'sort_order': sort_order, 'label': ''},
                )
                self.stdout.write(f'{"wired" if created else "ok"}: {theme_title} -> {program_title}')
