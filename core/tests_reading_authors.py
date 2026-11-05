from bs4 import BeautifulSoup
from django.template.loader import render_to_string
from django.test import TestCase
from home.models import HomePage
from multimedia.models import MultimediaPage
from people.models import PeoplePage, PersonPage

from .models import ContentPageAuthor, ContentPageEditor
from .templatetags.core_tags import split_aside_rows


class ReadingAsideLongGroupTests(TestCase):
    """Aside person groups of 5+ rendered people show the first 3 and fold the
    rest behind a "Show N more" toggle (BugHerd #523 revision). Groups of 1–4
    render every row with no toggle. Only rows that render count — archived
    people drop out before the split."""

    @classmethod
    def setUpTestData(cls):
        cls.home = HomePage.objects.get()
        cls.people = cls.home.add_child(instance=PeoplePage(title='People', slug='people'))
        cls.persons = [
            cls.people.add_child(instance=PersonPage(
                title=f'Person {i:02d}', slug=f'person-{i:02d}', position=f'Role {i:02d}'))
            for i in range(1, 22)
        ]
        cls.archived = [
            cls.people.add_child(instance=PersonPage(
                title=f'Archived {i}', slug=f'archived-{i}', archive=PersonPage.ArchiveStatus.ARCHIVED))
            for i in range(1, 4)
        ]

    # --- helpers -------------------------------------------------------------

    @staticmethod
    def authors(people):
        return [ContentPageAuthor(author=p) for p in people]

    @staticmethod
    def editors(people):
        return [ContentPageEditor(editor=p) for p in people]

    def render_group(self, items, group_key='authors', **extra):
        html = render_to_string('includes/reading_author_group.html', {
            'group_heading': 'About the Author',
            'group_items': items,
            'group_count': len(items),
            'group_key': group_key,
            **extra,
        })
        return BeautifulSoup(html, 'html.parser')

    @staticmethod
    def names(nodes):
        return [n.get_text(strip=True) for n in nodes]

    def visible_rows(self, soup):
        # Rows that are direct children of the group (always shown).
        group = soup.select_one('details.ds-reading__aside-group')
        return group.find_all('div', class_='ds-reading__author', recursive=False)

    def assert_no_toggle(self, soup, count):
        self.assertIsNone(soup.select_one('[data-ds-aside-toggle]'))
        self.assertIsNone(soup.select_one('.ds-reading__aside-more'))
        self.assertEqual(len(self.visible_rows(soup)), count)
        self.assertEqual(len(soup.select('.ds-reading__author')), count)

    def assert_folded(self, soup, total, group_key='authors', name_class='ds-reading__author-name'):
        hidden = total - 3
        visible = self.visible_rows(soup)
        self.assertEqual(len(visible), 3)
        more = soup.select_one('.ds-reading__aside-more')
        self.assertIsNotNone(more)
        self.assertEqual(more['id'], f'ds-reading-more-{group_key}')
        self.assertEqual(len(more.select('.ds-reading__author')), hidden)
        button = soup.select_one('[data-ds-aside-toggle]')
        self.assertIsNotNone(button)
        self.assertEqual(button.name, 'button')
        self.assertEqual(button['type'], 'button')
        self.assertEqual(button['aria-expanded'], 'false')
        self.assertEqual(button['aria-controls'], more['id'])
        self.assertEqual(button['data-ds-label-less'], 'Show fewer')
        self.assertEqual(button.get_text(' ', strip=True), f'Show {hidden} more')
        # The toggle follows the folded rows, inside the same group.
        self.assertIs(button.find_previous_sibling('div'), more)
        return visible, more

    # --- the split filter ----------------------------------------------------

    def test_split_filter_thresholds(self):
        for total, shown, more in ((1, 1, 0), (3, 3, 0), (4, 4, 0), (5, 3, 2), (21, 3, 18)):
            with self.subTest(total=total):
                rows = split_aside_rows(self.authors(self.persons[:total]))
                self.assertEqual((len(rows['shown']), len(rows['more'])), (shown, more))

    def test_split_filter_counts_only_renderable_rows(self):
        # 4 live + 3 archived authors = 7 rows, but only 4 render: no fold.
        items = self.authors(self.persons[:2] + self.archived + self.persons[2:4])
        rows = split_aside_rows(items)
        self.assertEqual(len(rows['shown']), 4)
        self.assertEqual(rows['more'], [])

    def test_split_filter_handles_empty(self):
        self.assertEqual(split_aside_rows(None), {'shown': [], 'more': []})

    # --- rendered markup -----------------------------------------------------

    def test_three_people_render_unchanged(self):
        soup = self.render_group(self.authors(self.persons[:3]))
        self.assert_no_toggle(soup, 3)

    def test_four_people_render_unchanged(self):
        soup = self.render_group(self.authors(self.persons[:4]))
        self.assert_no_toggle(soup, 4)

    def test_five_people_fold_two(self):
        soup = self.render_group(self.authors(self.persons[:5]))
        visible, more = self.assert_folded(soup, 5)
        self.assertEqual(self.names(v.select_one('.ds-reading__author-name') for v in visible),
                         ['Person 01', 'Person 02', 'Person 03'])
        self.assertEqual(self.names(more.select('.ds-reading__author-name')), ['Person 04', 'Person 05'])

    def test_twenty_one_people_fold_eighteen(self):
        soup = self.render_group(self.authors(self.persons))
        visible, more = self.assert_folded(soup, 21)
        folded = self.names(more.select('.ds-reading__author-name'))
        self.assertEqual(folded[0], 'Person 04')
        self.assertEqual(folded[-1], 'Person 21')
        # Every person renders exactly once, in order.
        self.assertEqual(self.names(soup.select('.ds-reading__author-name')),
                         [p.title for p in self.persons])

    def test_archived_people_do_not_count_toward_the_fold(self):
        # 7 rows, 3 archived: 4 render — every one shows, no toggle.
        items = self.authors(self.persons[:2] + self.archived + self.persons[2:4])
        soup = self.render_group(items)
        self.assert_no_toggle(soup, 4)
        self.assertNotIn('Archived', soup.get_text())

    def test_archived_people_are_left_out_of_the_hidden_count(self):
        # 8 rows, 2 archived inside the would-be folded part: 6 render → 3 + "Show 3 more".
        items = self.authors(self.persons[:4] + self.archived[:2] + self.persons[4:6])
        soup = self.render_group(items)
        _, more = self.assert_folded(soup, 6)
        self.assertEqual(self.names(more.select('.ds-reading__author-name')),
                         ['Person 04', 'Person 05', 'Person 06'])

    def test_editors_group(self):
        soup = self.render_group(self.editors(self.persons[:6]), group_key='editors',
                                 group_heading='About the Editor')
        self.assert_folded(soup, 6, group_key='editors')

    def test_editors_group_of_four_unchanged(self):
        soup = self.render_group(self.editors(self.persons[:4]), group_key='editors',
                                 group_heading='About the Editor')
        self.assert_no_toggle(soup, 4)

    def test_expert_card_mode(self):
        soup = self.render_group(self.authors(self.persons[:7]), card_mode='expert',
                                 group_heading='Experts / Host')
        self.assertIn('ds-reading__aside-group--expert', soup.select_one('details')['class'])
        _, more = self.assert_folded(soup, 7)
        # Every row is the shared expert card, folded ones included.
        self.assertEqual(len(soup.select('.ds-reading__author > .ds-expert-card')), 7)
        self.assertEqual(self.names(more.select('.ds-expert-card__name')),
                         ['Person 04', 'Person 05', 'Person 06', 'Person 07'])
        self.assertFalse(soup.select('.ds-reading__author-bio'))

    def test_expert_card_mode_of_four_unchanged(self):
        soup = self.render_group(self.authors(self.persons[:4]), card_mode='expert')
        self.assert_no_toggle(soup, 4)

    def test_guest_blocks_without_person_pages(self):
        stream_block = MultimediaPage._meta.get_field('podcast_guests').stream_block
        guests = stream_block.to_python(
            [{'type': 'guest', 'value': f'Plain Guest {i}'} for i in range(1, 4)]
            + [{'type': 'guest_page', 'value': {'guest': f'Block Guest {i}', 'guest_page': None,
                                                'image': None, 'bio': ''}} for i in range(1, 3)]
            + [{'type': 'guest_page', 'value': {'guest': '', 'guest_page': self.archived[0].pk,
                                                'image': None, 'bio': ''}}]
        )
        # 6 blocks; the last (archived page, no name) renders nothing → 5 rows.
        soup = self.render_group(guests, group_key='guests', group_heading='About the Speaker')
        _, more = self.assert_folded(soup, 5, group_key='guests')
        self.assertEqual(self.names(more.select('.ds-reading__author-name')),
                         ['Block Guest 1', 'Block Guest 2'])

    def test_reading_body_gives_each_group_its_own_id(self):
        html = render_to_string('includes/reading_body.html', {
            'body_html': '<p>Body</p>',
            'suppress_subscribe': True,
            'authors': self.authors(self.persons[:9]),
            'author_count': 9,
            'editors': self.editors(self.persons[9:14]),
            'editor_count': 5,
        })
        soup = BeautifulSoup(html, 'html.parser')
        buttons = soup.select('aside.ds-reading__aside [data-ds-aside-toggle]')
        self.assertEqual([b['aria-controls'] for b in buttons],
                         ['ds-reading-more-authors', 'ds-reading-more-editors'])
        self.assertEqual([b.get_text(' ', strip=True) for b in buttons], ['Show 6 more', 'Show 2 more'])
        for b in buttons:
            self.assertEqual(len(soup.select(f'#{b["aria-controls"]}')), 1)
