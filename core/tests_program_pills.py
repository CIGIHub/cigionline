"""Card pills in the program modules (BugHerd #519).

Program modules never pill a program: content cards in Program Grid, Programs
Carousel and the Program Spotlight show each item's own topics; cards that ARE
programs (theme Auto, manual multi-program) show no pill row; the Spotlight
panel has no pill repeating its heading. Resource modules are unchanged (they
already show topics).

Builds its own pages; core/tests.py is not touched.
"""

from datetime import timedelta

from bs4 import BeautifulSoup
from django.test import TestCase
from django.utils import timezone

from home.models import HomePage
from publications.models import PublicationListPage, PublicationPage, PublicationTypePage
from research.models import ProjectPage, ThemePage, ThemeProgram, TopicPage
from streams.blocks import (
    ProgramGridBlock,
    ProgramsCarouselBlock,
    ProgramSpotlightBlock,
    ResourceBentoBlock,
    program_card_pills,
    program_module_context,
)


def render(block, raw, page):
    return block.render(block.to_python(raw), context={'page': page})


def pills_by_card(resolved):
    """{card title: pills override} from program_module_context's ``cards``."""
    return {page.title: pills for page, pills in resolved['cards']}


def cards(html):
    """{card title: [pill labels]} for every .ds-card in the html. A card with
    no pill row maps to []."""
    soup = BeautifulSoup(html, 'html.parser')
    out = {}
    for card in soup.select('.ds-card'):
        title = card.select_one('.ds-card__title').get_text(strip=True)
        out[title] = [t.get_text(strip=True)
                      for t in card.select('.ds-card__pills .ds-tag__label')]
    return out


class ProgramModulePillTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.home = HomePage.objects.get()
        now = timezone.now()
        cls.theme = cls.home.add_child(instance=ThemePage(
            title='Digitalization, Security and Democracy', slug='dsd', accent='security'))
        cls.other_theme = cls.home.add_child(instance=ThemePage(
            title='Global Cooperation and Governance', slug='gcg', accent='governance'))
        cls.program = cls.home.add_child(instance=ProjectPage(
            title='Space Governance', slug='space-governance', publishing_date=now))
        cls.other_program = cls.home.add_child(instance=ProjectPage(
            title='Global AI Risks', slug='global-ai-risks', publishing_date=now))
        ThemeProgram.objects.create(theme=cls.theme, program=cls.program)
        ThemeProgram.objects.create(theme=cls.other_theme, program=cls.other_program)
        cls.emerging = cls.home.add_child(instance=TopicPage(
            title='Emerging Technologies', slug='emerging-technologies',
            program_theme=cls.theme))
        cls.multilateral = cls.home.add_child(instance=TopicPage(
            title='Multilateral Institutions', slug='multilateral-institutions',
            program_theme=cls.other_theme))
        # The program page itself carries topics: program-as-card must still
        # show no pill row (before #519 it fell back to these).
        cls.tag(cls.program, topics=[cls.emerging])
        cls.tag(cls.other_program, topics=[cls.multilateral])

        cls.policy_briefs = cls.home.add_child(instance=PublicationTypePage(
            title='Policy Briefs', slug='policy-briefs'))
        cls.publications = cls.home.add_child(instance=PublicationListPage(
            title='Publications', slug='publications'))
        cls.tagged = cls.publication(
            'Investment Treaties', now, projects=[cls.program],
            topics=[cls.emerging, cls.multilateral])
        cls.untagged = cls.publication(
            'Credit and Stability', now - timedelta(days=1), projects=[cls.program])
        cls.other = cls.publication(
            'AI Safety Report', now - timedelta(days=2), projects=[cls.other_program],
            topics=[cls.multilateral])

    @classmethod
    def tag(cls, page, projects=(), topics=()):
        page.projects.set(projects)
        page.topics.set(topics)
        page.save()  # ParentalManyToMany: set() persists on save
        return page.__class__.objects.get(pk=page.pk)

    @classmethod
    def publication(cls, title, date, **tags):
        page = cls.publications.add_child(instance=PublicationPage(
            title=title, publishing_date=date, publication_type=cls.policy_briefs))
        return cls.tag(page, **tags)

    # -- single program: content cards show the item's topics -----------------

    def test_card_pills_rule(self):
        self.assertIsNone(program_card_pills(self.tagged))
        self.assertIsNone(program_card_pills(self.untagged))
        self.assertEqual(program_card_pills(self.program), [])
        # Works on a non-specific Page too.
        self.assertEqual(program_card_pills(self.program.page_ptr), [])

    def test_single_program_context_defers_to_topics(self):
        for raw in ({'program_source': 'auto'},
                    {'program_source': 'manual', 'program': self.other_program.pk}):
            value = ProgramGridBlock().to_python(raw)
            resolved = program_module_context(value, self.program)
            self.assertTrue(resolved['cards'])
            for page, pills in resolved['cards']:
                self.assertIsNone(pills, page.title)

    def test_grid_auto_on_program_page_shows_topics(self):
        html = render(ProgramGridBlock(), {'program_source': 'auto'}, self.program)
        self.assertEqual(cards(html), {
            'Investment Treaties': ['Emerging Technologies', 'Multilateral Institutions'],
            'Credit and Stability': [],  # no topics → no pill row
        })
        self.assertNotIn('Space Governance', str(cards(html)))

    def test_carousel_auto_on_program_page_shows_topics(self):
        html = render(ProgramsCarouselBlock(), {'program_source': 'auto'}, self.program)
        self.assertEqual(cards(html), {
            'Investment Treaties': ['Emerging Technologies', 'Multilateral Institutions'],
            'Credit and Stability': [],
        })

    def test_carousel_manual_other_program_shows_topics(self):
        html = render(ProgramsCarouselBlock(),
                      {'program_source': 'manual', 'program': self.other_program.pk},
                      self.program)
        self.assertEqual(cards(html), {'AI Safety Report': ['Multilateral Institutions']})

    def test_untagged_item_has_no_pill_row(self):
        html = render(ProgramGridBlock(), {'program_source': 'auto'}, self.program)
        soup = BeautifulSoup(html, 'html.parser')
        untagged = [c for c in soup.select('.ds-card')
                    if c.select_one('.ds-card__title').get_text(strip=True) == 'Credit and Stability']
        self.assertEqual(len(untagged), 1)
        self.assertIsNone(untagged[0].select_one('.ds-card__pills'))

    # -- program-as-card: no pill row ----------------------------------------

    def test_theme_auto_program_cards_have_no_pills(self):
        value = ProgramGridBlock().to_python({'program_source': 'auto'})
        self.assertEqual(
            pills_by_card(program_module_context(value, self.theme)), {'Space Governance': []})
        html = render(ProgramGridBlock(), {'program_source': 'auto'}, self.theme)
        self.assertEqual(cards(html), {'Space Governance': []})
        self.assertNotIn('ds-card__pills', html)

    def test_manual_multi_program_cards_have_no_pills(self):
        raw = {'program_source': 'manual',
               'programs': [self.program.pk, self.other_program.pk]}
        self.assertEqual(
            pills_by_card(program_module_context(ProgramsCarouselBlock().to_python(raw), self.home)),
            {'Space Governance': [], 'Global AI Risks': []})
        for block in (ProgramGridBlock(), ProgramsCarouselBlock()):
            html = render(block, raw, self.home)
            self.assertEqual(cards(html), {'Space Governance': [], 'Global AI Risks': []})
            self.assertNotIn('ds-card__pills', html)

    def test_handpicked_program_items_have_no_pills(self):
        # The /experts/ "Explore Our Research Areas" shape (staging page 19):
        # program source Auto on a page that is not a program, so no program
        # resolves, and the cards are hand-picked items that are program pages.
        # Before #519 these fell back to the program pages' own topics.
        raw = {'program_source': 'auto', 'mode': 'manual',
               'items': [self.program.pk, self.other_program.pk, self.tagged.pk]}
        for block in (ProgramGridBlock(), ProgramsCarouselBlock()):
            resolved = program_module_context(block.to_python(raw), self.home)
            self.assertIsNone(resolved['program'])
            html = render(block, raw, self.home)
            self.assertEqual(cards(html), {
                'Space Governance': [],
                'Global AI Risks': [],
                # A content item in the same list still shows its topics.
                'Investment Treaties': ['Emerging Technologies', 'Multilateral Institutions'],
            })

    # -- Program Spotlight ----------------------------------------------------

    def test_spotlight_entry_has_no_program_pill(self):
        context = ProgramSpotlightBlock().get_context(
            ProgramSpotlightBlock().to_python({}), {'page': self.home})
        self.assertTrue(context['spotlight_programs'])
        for entry in context['spotlight_programs']:
            self.assertNotIn('card_pill', entry)
            for page, pills in entry['cards']:
                self.assertIsNone(pills, page.title)

    def test_spotlight_panel_has_no_pill_and_cards_show_topics(self):
        html = render(ProgramSpotlightBlock(), {}, self.home)
        soup = BeautifulSoup(html, 'html.parser')
        bodies = soup.select('.ds-program-spotlight__panel-body')
        self.assertEqual(len(bodies), 2)  # one panel per live program
        for body in bodies:
            self.assertEqual(body.select('.ds-tag'), [])
            # The heading is now the panel body's first element.
            self.assertIn('ds-program-spotlight__panel-heading',
                          body.find(True)['class'])
        self.assertEqual(cards(html), {
            'Investment Treaties': ['Emerging Technologies', 'Multilateral Institutions'],
            'Credit and Stability': [],
            'AI Safety Report': ['Multilateral Institutions'],
        })
        # No program name in any pill anywhere in the module.
        labels = [t.get_text(strip=True) for t in soup.select('.ds-tag__label')]
        self.assertNotIn('Space Governance', labels)
        self.assertNotIn('Global AI Risks', labels)

    def test_spotlight_manual_cards_show_topics(self):
        raw = {'programs': [{'program': self.program.pk,
                             'content_pages': [self.untagged.pk, self.other.pk]}]}
        html = render(ProgramSpotlightBlock(), raw, self.home)
        self.assertEqual(cards(html), {
            'Credit and Stability': [],
            'AI Safety Report': ['Multilateral Institutions'],
        })
        # The card chooser takes any page: a hand-picked program page shows no pill.
        raw = {'programs': [{'program': self.program.pk,
                             'content_pages': [self.other_program.pk, self.tagged.pk]}]}
        html = render(ProgramSpotlightBlock(), raw, self.home)
        self.assertEqual(cards(html), {
            'Global AI Risks': [],
            'Investment Treaties': ['Emerging Technologies', 'Multilateral Institutions'],
        })

    # -- Resource modules unchanged (regression guard) ------------------------

    def test_resource_bento_still_shows_topics(self):
        for page, expected in (
            (self.program, {'Investment Treaties', 'Credit and Stability'}),
            (self.home, {'Investment Treaties', 'Credit and Stability', 'AI Safety Report'}),
        ):
            html = render(ResourceBentoBlock(), {'mode': 'auto'}, page)
            found = cards(html)
            self.assertEqual(set(found), expected)
            self.assertEqual(found['Investment Treaties'],
                             ['Emerging Technologies', 'Multilateral Institutions'])
            self.assertEqual(found['Credit and Stability'], [])
            if 'AI Safety Report' in found:
                self.assertEqual(found['AI Safety Report'], ['Multilateral Institutions'])
