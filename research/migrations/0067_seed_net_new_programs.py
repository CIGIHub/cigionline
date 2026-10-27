from django.db import migrations

# The 4 net-new program pages, confirmed by the IA hierarchy image (2026-06-11).
#
# REWRITTEN pre-staging (2026-07-08): the original imported live models —
# broken on any content DB migrating through this point (columns from later
# migrations don't exist yet) — and used Page.add_child, which historical
# models don't have. Page-shell creation now lives in the idempotent
# `manage.py seed_net_new_programs` command (run it after migrate; it also
# wires the ThemeProgram rows). This migration keeps only the safe part on
# historical models: the National Security sort-order bump that makes room
# for Freedom of Thought, and ThemeProgram wiring for programs that already
# exist. See docs/redesign/taxonomy-rollout-summary.md §5.
#
# (theme_title, [ (program_title, sort_order), ... ])
PROGRAMS = [
    ('Digitalization, Security and Democracy', [
        ('Freedom of Thought', 2),  # between Space Governance 4.0 (1) and National Security (bumped to 3)
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
        # tolerate straight-vs-curly apostrophe drift
        qs = model.objects.filter(title=title.replace('’', "'"))
    return qs.first()


def seed(apps, schema_editor):
    ThemePage = apps.get_model('research', 'ThemePage')
    ProjectPage = apps.get_model('research', 'ProjectPage')
    ThemeProgram = apps.get_model('research', 'ThemeProgram')

    # DSD: Freedom of Thought slots in at order 2, so push National Security to 3.
    dsd = get_by_title(ThemePage, 'Digitalization, Security and Democracy')
    if dsd is not None:
        ns = ThemeProgram.objects.filter(theme=dsd, sort_order=2).select_related('program').first()
        if ns is not None and 'Freedom of Thought' not in ns.program.title:
            ns.sort_order = 3
            ns.save(update_fields=['sort_order'])

    # Wire ThemeProgram rows for any of the 4 that already exist as pages;
    # missing pages (the normal case) are created + wired by the
    # seed_net_new_programs command after migrate.
    for theme_title, programs in PROGRAMS:
        theme = get_by_title(ThemePage, theme_title)
        if theme is None:
            continue
        for program_title, sort_order in programs:
            program = get_by_title(ProjectPage, program_title)
            if program is None:
                continue
            ThemeProgram.objects.get_or_create(
                theme=theme,
                program=program,
                defaults={'sort_order': sort_order, 'label': ''},
            )


def unseed(apps, schema_editor):
    ThemePage = apps.get_model('research', 'ThemePage')
    ProjectPage = apps.get_model('research', 'ProjectPage')
    ThemeProgram = apps.get_model('research', 'ThemeProgram')

    # Unwire the ThemeProgram rows only. Page shells (if the command created
    # them) are deliberately left in place — deleting pages through historical
    # models would bypass Wagtail's treebeard bookkeeping.
    titles = [t for _, progs in PROGRAMS for t, _ in progs]
    for title in titles:
        program = get_by_title(ProjectPage, title)
        if program is not None:
            ThemeProgram.objects.filter(program=program).delete()

    # restore National Security to order 2
    dsd = get_by_title(ThemePage, 'Digitalization, Security and Democracy')
    if dsd is not None:
        ns = ThemeProgram.objects.filter(theme=dsd, sort_order=3).first()
        if ns is not None:
            ns.sort_order = 2
            ns.save(update_fields=['sort_order'])


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0066_seed_theme_programs'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
