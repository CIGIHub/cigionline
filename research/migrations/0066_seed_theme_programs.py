from django.db import migrations

# Theme accents + the confirmed theme->program rows (IA copybook, 2026-06-11).
# Programs marked net-new in docs/redesign/migration-strategy.md §4 are not
# seeded — editors create the pages and add rows via the Programs InlinePanel.
THEMES = {
    'AI and Transformative Technology': {
        'accent': 'ai-tech',
        'programs': [
            ('AI Empowerment for a Prosperous Future', 'AI Empowerment'),
            ('Responsible Technology', ''),
            ('Global AI Risks Initiative', 'Global AI Risks'),
        ],
    },
    'Data, Economy, Society': {
        'accent': 'data-economy',
        'programs': [
            ('Digital Assets in a Deglobalized World', 'Governance of Digital Money and Assets'),
            ('Next-Generation Economies: Middle Powers in a Changing World', 'Next-Generation Economies'),
            ('Africa’s Digital Transformation', ''),
        ],
    },
    'Digitalization, Security and Democracy': {
        'accent': 'security',
        'programs': [
            ('Supporting Safer Digital Spaces', ''),
            ('Space Governance 4.0', ''),
            # 'Freedom of Thought' — net-new page, added by editors
            ('Strengthening Canada’s National Security in a Complex World', 'National Security and Cybersecurity'),
        ],
    },
    'Global Cooperation and Governance': {
        'accent': 'governance',
        'programs': [
            # All net-new pages, added by editors:
            # 'India and China in a Multipolar World'
            # 'Multilateral and Institutional Reform'
            # 'Canada-US Relations in the Second Century'
        ],
    },
}


def get_by_title(model, title):
    qs = model.objects.filter(title=title)
    if not qs.exists():
        # tolerate straight-vs-curly apostrophe drift
        qs = model.objects.filter(title=title.replace('’', "'"))
    return qs.first()


def seed(apps, schema_editor):
    # Historical models only: importing research.models here compiles queries
    # against the CURRENT model (including columns added by later migrations,
    # e.g. projectpage.surface from 0069) — UndefinedColumn on any DB with
    # content migrating through this point.
    ThemePage = apps.get_model('research', 'ThemePage')
    ProjectPage = apps.get_model('research', 'ProjectPage')
    ThemeProgram = apps.get_model('research', 'ThemeProgram')

    for theme_title, config in THEMES.items():
        theme = get_by_title(ThemePage, theme_title)
        if theme is None:
            print(f'ThemePage not found, skipping: {theme_title}')
            continue

        if not theme.accent:
            theme.accent = config['accent']
            theme.save(update_fields=['accent'])

        for sort_order, (program_title, label) in enumerate(config['programs']):
            program = get_by_title(ProjectPage, program_title)
            if program is None:
                print(f'ProjectPage not found, skipping: {program_title}')
                continue
            ThemeProgram.objects.get_or_create(
                theme=theme,
                program=program,
                defaults={'sort_order': sort_order, 'label': label},
            )


def unseed(apps, schema_editor):
    ThemePage = apps.get_model('research', 'ThemePage')
    ThemeProgram = apps.get_model('research', 'ThemeProgram')

    ThemeProgram.objects.all().delete()
    ThemePage.objects.update(accent='')


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0065_themepage_accent_themeprogram'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
