from django.db import migrations


# (slug, name, [link titles]) for the four design-system footer columns.
# Column links start as placeholders ('#') — they preserve the current footer
# content and are now editable under Snippets -> Menus.
FOOTER_COLUMNS = [
    ('footer-research', 'Data, Economy & Society', [
        'Data, Economy & Society',
        'AI & Transformative Technology',
        'Digitization, Security & Democracy',
        'Global Cooperation & Governance',
    ]),
    ('footer-experts-events', 'Experts, Opinions, Events', [
        'Experts',
        'Opinions',
        'Events',
        'Venue Rentals',
        'For Media & Press',
    ]),
    ('footer-digital-policy-hub', 'Digital Policy Hub', [
        'About the Digital Policy Hub',
        'Cohort (Current & Alumni)',
        'Working Papers',
        'Speakers',
        'Application & Program Information',
    ]),
    ('footer-about', 'About', [
        'About CIGI',
        'Leadership, Partners & Team',
        'CIGI Campus',
        'Media and CIGI News',
        'Careers',
        'Contact',
    ]),
]

# Legal links have real destinations.
FOOTER_LEGAL = ('footer-legal', 'Footer Legal', [
    ('Privacy Notice', '/privacy-notice/'),
    ('Terms of Service', '/terms-of-service/'),
])

ALL_SLUGS = [slug for slug, _, _ in FOOTER_COLUMNS] + [FOOTER_LEGAL[0]]


def populate_footer_menus(apps, schema_editor):
    Menu = apps.get_model('menus', 'Menu')
    MenuItem = apps.get_model('menus', 'MenuItem')

    for slug, name, links in FOOTER_COLUMNS:
        if Menu.objects.filter(slug=slug).exists():
            continue
        menu = Menu.objects.create(name=name, slug=slug)
        for order, title in enumerate(links):
            MenuItem.objects.create(menu=menu, title=title, link_url='#', sort_order=order)

    legal_slug, legal_name, legal_links = FOOTER_LEGAL
    if not Menu.objects.filter(slug=legal_slug).exists():
        menu = Menu.objects.create(name=legal_name, slug=legal_slug)
        for order, (title, url) in enumerate(legal_links):
            MenuItem.objects.create(menu=menu, title=title, link_url=url, sort_order=order)


def remove_footer_menus(apps, schema_editor):
    Menu = apps.get_model('menus', 'Menu')
    Menu.objects.filter(slug__in=ALL_SLUGS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('menus', '0003_increase_menu_item_title_length'),
    ]

    operations = [
        migrations.RunPython(populate_footer_menus, remove_footer_menus),
    ]
