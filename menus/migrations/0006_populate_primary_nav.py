from django.db import migrations


# Slugs created by this seed (used for the idempotency guard + reverse).
NAV_SLUGS = [
    'primary-nav',
    'nav-topics', 'nav-experts', 'nav-events', 'nav-dph', 'nav-our-work',
    'nav-about', 'nav-about-cigi', 'nav-about-leadership', 'nav-about-campus', 'nav-about-media',
]


def populate_primary_nav(apps, schema_editor):
    Menu = apps.get_model('menus', 'Menu')
    MenuItem = apps.get_model('menus', 'MenuItem')

    if Menu.objects.filter(slug='primary-nav').exists():
        return  # idempotent

    def menu(slug, name):
        return Menu.objects.create(slug=slug, name=name)

    def item(parent, order, title, url='#', desc='', submenu=None):
        MenuItem.objects.create(
            menu=parent, sort_order=order, title=title,
            link_url=url, description=desc, submenu=submenu,
        )

    def column(parent, order, title, links, submenu_slug, submenu_name):
        sub = menu(submenu_slug, submenu_name)
        for i, t in enumerate(links):
            item(sub, i, t)
        item(parent, order, title, submenu=sub)

    # --- About: full-width 4-column panel (columns each have their own link list) ---
    about = menu('nav-about', 'About')
    column(about, 0, 'About CIGI',
           ['Mission, Vision & Strategic Plan', 'History', 'Annual Reports', 'Careers', 'Contact'],
           'nav-about-cigi', 'About — About CIGI')
    column(about, 1, 'Leadership, Partners & Team',
           ['Senior Management & Board', 'Partners', 'Staff Directory'],
           'nav-about-leadership', 'About — Leadership')
    column(about, 2, 'CIGI Campus',
           ['Venue Rentals'],
           'nav-about-campus', 'About — CIGI Campus')
    column(about, 3, 'Media and CIGI News',
           ['CIGI News', 'In the News', 'CIGI Podcast'],
           'nav-about-media', 'About — Media and CIGI News')

    # --- Compact single-section panels (flat link lists) ---
    experts = menu('nav-experts', 'Experts')
    item(experts, 0, 'For Media')

    events = menu('nav-events', 'Events')
    item(events, 0, 'Venue Rentals')

    dph = menu('nav-dph', 'Digital Policy Hub')
    for i, t in enumerate([
        'About the Digital Policy Hub', 'Cohort (Current & Alumni)',
        'Working Papers', 'Speakers', 'Application & Program Information',
    ]):
        item(dph, i, t)

    # Our Work — contents pending its Figma panel; placeholder so the bar label renders.
    our_work = menu('nav-our-work', 'Our Work')

    # Topics — marker submenu; the template renders the live research taxonomy here,
    # not these items (kept empty on purpose).
    topics = menu('nav-topics', 'Topics (dynamic)')

    # --- Primary nav: the 7 top-level items in order ---
    nav = menu('primary-nav', 'Primary Navigation')
    item(nav, 0, 'Topics', submenu=topics)
    item(nav, 1, 'Experts', url='/experts/', submenu=experts)
    item(nav, 2, 'Opinions')
    item(nav, 3, 'Events', url='/events/', submenu=events)
    item(nav, 4, 'Digital Policy Hub', submenu=dph)
    item(nav, 5, 'About', submenu=about)
    item(nav, 6, 'Our Work', submenu=our_work)


def remove_primary_nav(apps, schema_editor):
    Menu = apps.get_model('menus', 'Menu')
    Menu.objects.filter(slug__in=NAV_SLUGS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('menus', '0005_menuitem_description'),
    ]

    operations = [
        migrations.RunPython(populate_primary_nav, remove_primary_nav),
    ]
