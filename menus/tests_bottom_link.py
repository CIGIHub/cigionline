"""
Header dropdown "Bottom link" (menus.Menu.bottom_link_label/_page/_url, BugHerd #539).

Renders the real `includes/header.html` against a hand-built `primary-nav` and
checks every place a dropdown renders: the three desktop panel branches
(code-built `nav-topics`, columns, compact) and the mobile drawer.
"""
from bs4 import BeautifulSoup
from django.db import connection
from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase
from django.test.utils import CaptureQueriesContext
from wagtail.models import Page, Site

from .models import Menu, MenuItem
from .templatetags.menu_tags import get_menu
from .wagtail_hooks import MenuViewSet

LABEL = 'Browse All Archived Topics'


class MenuBottomLinkTests(TestCase):

    def setUp(self):
        # Replace the 0006 seed nav with a known fixture.
        Menu.objects.filter(slug__in=[
            'primary-nav', 'nav-topics', 'nav-experts', 'nav-events', 'nav-dph',
            'nav-our-work', 'nav-about', 'nav-about-cigi', 'nav-about-leadership',
            'nav-about-campus', 'nav-about-media',
        ]).delete()
        root = Site.objects.get(is_default_site=True).root_page
        self.archive = root.add_child(instance=Page(title='Archived Topics', slug='archived-topics'))
        self.draft = root.add_child(instance=Page(title='Draft', slug='draft-archive', live=False))

        self.nav = Menu.objects.create(name='Primary', slug='primary-nav')

        # Topics (standard): columns, each theme with its own link list.
        self.topics = Menu.objects.create(name='Topics (standard)', slug='nav-topics-standard')
        for i, theme in enumerate(['Theme A', 'Theme B']):
            sub = Menu.objects.create(name=f'Topic - {theme}', slug=f'topic-{i}')
            MenuItem.objects.create(menu=sub, sort_order=0, title=f'{theme} program', link_url=f'/p{i}/')
            MenuItem.objects.create(menu=self.topics, sort_order=i, title=theme, link_url=f'/t{i}/', submenu=sub)
        MenuItem.objects.create(menu=self.nav, sort_order=0, title='Topics', link_url='#', submenu=self.topics)

        # Events: compact single list.
        self.events = Menu.objects.create(name='Events', slug='nav-events')
        MenuItem.objects.create(menu=self.events, sort_order=0, title='Venue Rentals', link_url='/venue/')
        MenuItem.objects.create(menu=self.nav, sort_order=1, title='Events', link_url='/events/', submenu=self.events)

        # Code-built taxonomy panel (no ThemePages in the test DB: zero columns).
        self.code_topics = Menu.objects.create(name='Topics (dynamic)', slug='nav-topics')
        MenuItem.objects.create(menu=self.nav, sort_order=2, title='Code Topics', link_url='#', submenu=self.code_topics)

        # About: columns, never given a bottom link here.
        self.about = Menu.objects.create(name='About', slug='nav-about')
        about_sub = Menu.objects.create(name='About - CIGI', slug='nav-about-cigi')
        MenuItem.objects.create(menu=about_sub, sort_order=0, title='History', link_url='/history/')
        MenuItem.objects.create(menu=self.about, sort_order=0, title='About CIGI', link_url='/about/', submenu=about_sub)
        MenuItem.objects.create(menu=self.nav, sort_order=3, title='About', link_url='/about/', submenu=self.about)

    # --- helpers ---------------------------------------------------------------
    def render(self):
        request = RequestFactory().get('/')
        return render_to_string('includes/header.html', {}, request=request)

    def soup(self):
        return BeautifulSoup(self.render(), 'html.parser')

    def set_link(self, menu, label=LABEL, page=None, url=''):
        menu.bottom_link_label = label
        menu.bottom_link_page = page
        menu.bottom_link_url = url
        menu.save()

    def desktop_panel(self, soup, n):
        return soup.find(id=f'ds-nav-panel-{n}')

    def drawer_section(self, soup, title):
        for details in soup.select('.ds-header__drawer details.ds-header__m-item'):
            if details.summary.get_text(strip=True) == title:
                return details.select_one('.ds-header__m-sub')
        raise AssertionError(f'no drawer section {title!r}')

    # --- desktop ---------------------------------------------------------------
    def test_columns_panel_renders_foot_after_columns(self):
        self.set_link(self.topics, page=self.archive)
        soup = self.soup()
        panel = self.desktop_panel(soup, 1)
        self.assertIn('ds-header__panel--full', panel['class'])
        children = panel.find_all(recursive=False)
        self.assertEqual([c['class'][0] for c in children], ['ds-header__panel-inner', 'ds-header__panel-foot'])
        foot = children[1]
        self.assertIn('ds-container', foot['class'])
        cta = foot.select_one('a.ds-button.ds-button--tertiary.ds-header__panel-cta')
        self.assertEqual(cta.get_text(strip=True), LABEL)
        self.assertTrue(cta['href'].endswith('/archived-topics/'))
        self.assertIsNotNone(cta.select_one('svg.ds-button__icon'))
        # Not a column, not a heading; once in the desktop nav.
        self.assertEqual(len(panel.select('.ds-header__panel-col')), 2)
        self.assertNotIn(LABEL, [h.get_text(strip=True) for h in soup.select('.ds-header__panel-heading')])
        self.assertEqual(len(soup.select('.ds-header__nav .ds-header__panel-cta')), 1)
        # Only the Topics dropdown has one.
        for n in (2, 3, 4):
            self.assertIsNone(self.desktop_panel(soup, n).select_one('.ds-header__panel-foot'))

    def test_compact_panel_renders_foot_last_in_column(self):
        self.set_link(self.events, label='All events', url='/events/archive/')
        panel = self.desktop_panel(self.soup(), 2)
        self.assertIn('ds-header__panel--compact', panel['class'])
        col = panel.select_one('.ds-header__panel-col')
        last = col.find_all(recursive=False)[-1]
        self.assertEqual(last['class'], ['ds-header__panel-foot'])  # no ds-container in a compact box
        cta = last.select_one('a.ds-header__panel-cta')
        self.assertEqual(cta['href'], '/events/archive/')
        self.assertEqual(cta.get_text(strip=True), 'All events')
        # The links list is unchanged and precedes the foot.
        self.assertEqual([a.get_text() for a in col.select('.ds-header__panel-links a')], ['Venue Rentals'])

    def test_code_built_topics_panel_renders_foot(self):
        self.set_link(self.code_topics, page=self.archive)
        panel = self.desktop_panel(self.soup(), 3)
        children = panel.find_all(recursive=False)
        self.assertEqual([c['class'][0] for c in children], ['ds-header__panel-inner', 'ds-header__panel-foot'])
        self.assertTrue(children[1].a['href'].endswith('/archived-topics/'))

    # --- mobile ----------------------------------------------------------------
    def test_mobile_link_is_last_in_section(self):
        self.set_link(self.topics, page=self.archive)
        self.set_link(self.events, label='All events', url='/events/archive/')
        self.set_link(self.code_topics, label='Code', url='/code/')
        soup = self.soup()
        for title, label in (('Topics', LABEL), ('Events', 'All events'), ('Code Topics', 'Code')):
            sub = self.drawer_section(soup, title)
            last = sub.find_all(recursive=False)[-1]
            self.assertEqual(last.name, 'a')
            self.assertEqual(last['class'], ['ds-header__m-cta'])
            self.assertEqual(last.get_text(strip=True), label)
        topics = self.drawer_section(soup, 'Topics')
        self.assertNotIn(LABEL, [g.get_text(strip=True) for g in topics.select('.ds-header__m-group')])
        self.assertEqual(len(soup.select('.ds-header__drawer .ds-header__m-cta')), 3)
        self.assertIsNone(self.drawer_section(soup, 'About').select_one('.ds-header__m-cta'))

    # --- blank / precedence / publish state -------------------------------------
    def test_blank_or_half_set_link_leaves_markup_unchanged(self):
        baseline = self.render()
        self.assertNotIn('ds-header__panel-foot', baseline)
        self.assertNotIn('ds-header__m-cta', baseline)
        for kwargs in (
            {'label': ''},                            # nothing set
            {'label': LABEL},                         # label, no link
            {'label': '', 'page': self.archive},      # page, no label
            {'label': '', 'url': '/archived/'},       # URL, no label
            {'label': '   ', 'url': '/archived/'},    # whitespace label
            {'label': LABEL, 'page': self.draft},     # unpublished page
            {'label': LABEL, 'page': self.draft, 'url': '/fallback/'},  # page wins, even unpublished
        ):
            for menu in (self.topics, self.events, self.code_topics):
                self.set_link(menu, **kwargs)
            with self.subTest(**{k: str(v) for k, v in kwargs.items()}):
                self.assertEqual(self.render(), baseline)

    def test_page_wins_over_url(self):
        self.set_link(self.topics, page=self.archive, url='/somewhere-else/')
        soup = self.soup()
        hrefs = [a['href'] for a in soup.select('.ds-header__panel-cta, .ds-header__m-cta')]
        self.assertEqual(len(hrefs), 2)
        for href in hrefs:
            self.assertTrue(href.endswith('/archived-topics/'), href)
        self.assertNotIn('/somewhere-else/', str(soup))

    def test_bottom_link_helper(self):
        self.assertIsNone(self.topics.bottom_link)
        self.set_link(self.topics, url=' /x/ ')
        self.assertEqual(self.topics.bottom_link, {'label': LABEL, 'page': None, 'url': '/x/'})
        self.set_link(self.topics, page=self.archive, url='/x/')
        self.assertEqual(self.topics.bottom_link['page'].pk, self.archive.pk)
        self.set_link(self.topics, page=self.draft, url='/x/')
        self.assertIsNone(self.topics.bottom_link)

    def test_deleting_the_page_keeps_the_menu(self):
        self.set_link(self.topics, page=self.archive)
        self.archive.delete()
        self.topics.refresh_from_db()
        self.assertIsNone(self.topics.bottom_link_page_id)  # SET_NULL, not CASCADE
        self.assertIsNone(self.topics.bottom_link)

    # --- queries -----------------------------------------------------------------
    def test_bottom_link_pages_are_prefetched(self):
        """Reading submenu.bottom_link_page costs no per-dropdown query."""
        def count():
            with CaptureQueriesContext(connection) as ctx:
                self.render()
            return len(ctx.captured_queries)

        self.render()  # warm site-root-path caches
        blank = count()
        self.set_link(self.topics, page=self.archive)
        one = count()
        self.set_link(self.events, page=self.archive)
        self.set_link(self.code_topics, page=self.archive)
        self.set_link(self.about, page=self.archive)
        # One batched prefetch for the bottom-link pages, whatever the number of dropdowns.
        self.assertLessEqual(one, blank + 1)
        with self.assertNumQueries(one):
            self.render()
        menu = get_menu('primary-nav')
        with self.assertNumQueries(0):
            links = [i.submenu.bottom_link for i in menu.menu_items.all()]
        self.assertEqual(len([lnk for lnk in links if lnk]), 4)

    # --- admin -------------------------------------------------------------------
    def test_admin_form_has_bottom_link_panel(self):
        handler = MenuViewSet().get_edit_handler()
        form_class = handler.get_form_class()
        for field in ('bottom_link_label', 'bottom_link_page', 'bottom_link_url'):
            self.assertIn(field, form_class.base_fields)
        headings = [getattr(p, 'heading', '') for p in handler.children]
        self.assertIn('Bottom link', headings)
        form = form_class(instance=self.topics, data={
            'name': self.topics.name, 'slug': self.topics.slug,
            'bottom_link_label': LABEL, 'bottom_link_page': self.archive.pk, 'bottom_link_url': '',
            'menu_items-TOTAL_FORMS': '0', 'menu_items-INITIAL_FORMS': '0',
            'menu_items-MIN_NUM_FORMS': '0', 'menu_items-MAX_NUM_FORMS': '1000',
        })
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.topics.refresh_from_db()
        self.assertEqual(self.topics.bottom_link_page_id, self.archive.pk)
        # Settings -> Menus -> edit renders the panel and its help text.
        from django.contrib.auth import get_user_model
        from django.urls import reverse
        self.client.force_login(get_user_model().objects.create_superuser(username='editor', password=None))
        response = self.client.get(reverse(f'{MenuViewSet().url_namespace}:edit', args=[self.topics.pk]))
        self.assertContains(response, 'name="bottom_link_label"')
        self.assertContains(response, 'name="bottom_link_page"')
        self.assertContains(response, 'name="bottom_link_url"')
        self.assertContains(response, "under this dropdown&#x27;s columns (desktop)")
