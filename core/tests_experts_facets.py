from django.test import RequestFactory, TestCase
from home.models import HomePage
from people.models import PeoplePage, PersonListPage, PersonPage, PersonType
from research.models import ThemePage, TopicPage
from streams.blocks import FacetedListingBlock

from .faceted_listing import _topics_in, build_listing_context
from .heroes import person_hero_data


class ExpertsThemeTopicFacetTests(TestCase):
    """/experts/ filters by Theme and by Topic as separate facets (John,
    BugHerd #521). The facet labelled Topic used to list the research themes;
    Theme now lists them on `experts-theme`, and Topic lists the topics experts
    actually carry on `experts-topic`. Old links with a theme id in
    `experts-topic` still filter by that theme. Builds its own pages — no
    people.json fixture."""

    # Staging's block on /experts/ (page 19).
    STAGING_LISTING = {
        'card_type': 'expert', 'prefix': 'experts', 'facets': ['topic', 'type'],
        'show_filters': True, 'show_search': True, 'heading': 'Browse All Experts',
        'person_type': 'dph_fellow'}

    @staticmethod
    def listing(**value):
        block = FacetedListingBlock()
        return block.get_prep_value(block.to_python(value))

    @classmethod
    def setUpTestData(cls):
        cls.home = HomePage.objects.get()
        cls.value = cls.listing(**cls.STAGING_LISTING)
        cls.page = cls.home.add_child(instance=PersonListPage(
            title='Experts', slug='experts',
            person_list_page_type=PersonListPage.PersonListPageType.EXPERTS,
            body=[{'type': 'faceted_listing', 'value': cls.value}]))
        cls.people = cls.home.add_child(instance=PeoplePage(title='People', slug='people'))
        cls.ai = cls.home.add_child(instance=ThemePage(
            title='AI and Transformative Technology', slug='ai', accent='security'))
        cls.data = cls.home.add_child(instance=ThemePage(
            title='Data, Economy and Society', slug='data', accent='security'))
        # A live theme no expert reaches, and an archived one an expert does.
        cls.security = cls.home.add_child(instance=ThemePage(
            title='Digitalization, Security and Democracy', slug='security',
            accent='security'))
        cls.old = cls.home.add_child(instance=ThemePage(
            title='Retired Theme', slug='retired', accent='security', archive=1))

        def topic(title, theme=None, **kw):
            return cls.home.add_child(instance=TopicPage(
                title=title, slug='topic-' + title.lower().replace(' ', '-').replace(',', ''),
                program_theme=theme, **kw))

        cls.ai_topic = topic('AI', cls.ai)
        cls.quantum = topic('Quantum', cls.ai)
        cls.data_topic = topic('Data Governance', cls.data)
        cls.privacy = topic('Privacy', cls.data)
        cls.uncarried = topic('Digital Economy', cls.data)
        cls.unmapped = topic('India, China and Africa')
        cls.legacy = topic('Legacy Programme', cls.old)
        cls.archived = topic('Archived Topic', archive=1)
        cls.draft = topic('Unpublished Topic', live=False)
        cls.trade = topic('Trade', cls.security)

        cls.senior = PersonType.objects.get(name='Senior Fellow')
        tags = [
            [cls.ai_topic], [cls.ai_topic], [cls.ai_topic], [cls.ai_topic],   # e00-e03
            [cls.quantum], [cls.quantum],                                     # e04-e05
            [cls.data_topic], [cls.data_topic],                               # e06-e07
            [cls.privacy, cls.ai_topic],                                      # e08
            [cls.archived, cls.draft],                                        # e09
            [cls.unmapped, cls.legacy],                                       # e10
            [],                                                               # e11
        ]
        cls.experts = [
            cls.make_person('e%02d' % i, ['Expert'] + (['Senior Fellow'] if i in (0, 6) else []),
                            topics)
            for i, topics in enumerate(tags)]
        # Staff carry topics too; they are not experts, so Trade (and its
        # theme) must not reach the experts' facets.
        cls.make_person('staffer', ['Staff'], [cls.trade])

    @classmethod
    def make_person(cls, slug, types, topics=()):
        person = cls.people.add_child(instance=PersonPage(
            title=slug, slug=slug, last_name=slug))
        person.person_types.set([PersonType.objects.get(name=name) for name in types])
        person.save()
        person.derived_topics.set(topics)
        return PersonPage.objects.get(pk=person.pk)

    def ctx(self, value=None, prefix='experts', **params):
        request = RequestFactory().get(
            '/experts/', {'%s-%s' % (prefix, k): v for k, v in params.items()})
        return build_listing_context(request, value or self.value)

    @staticmethod
    def facet(context, key):
        return next((f for f in context['router_facets'] if f['key'] == key), None)

    @staticmethod
    def slugs(context):
        return sorted(p.slug for p in context['router_results'])

    def expert_slugs(self, *indexes):
        return sorted(self.experts[i].slug for i in indexes)

    def checked(self, context, key):
        return [o['label'] for o in self.facet(context, key)['options'] if o['checked']]

    # --- facet shape ----------------------------------------------------------

    def test_facets_are_type_theme_topic(self):
        context = self.ctx()
        self.assertEqual([f['key'] for f in context['router_facets']],
                         ['type', 'theme', 'topic'])
        self.assertEqual([f['label'] for f in context['router_facets']],
                         ['Type', 'Theme', 'Topic'])
        self.assertTrue(all(f['open'] for f in context['router_facets']))
        self.assertTrue(all(len(f['options']) > 1 for f in context['router_facets']))
        self.assertEqual(context['router_total'], 12)
        self.assertFalse(context['router_has_filters'])

    def test_theme_lists_only_live_themes_experts_carry(self):
        facet = self.facet(self.ctx(), 'theme')
        # Tree order; no uncarried Security, no archived Retired Theme, and the
        # staff member's Trade theme is not an expert's.
        self.assertEqual([o['label'] for o in facet['options']],
                         ['AI and Transformative Technology', 'Data, Economy and Society'])
        self.assertEqual([o['value'] for o in facet['options']], [self.ai.pk, self.data.pk])

    def test_topic_lists_only_active_topics_experts_carry(self):
        facet = self.facet(self.ctx(), 'topic')
        # A–Z, as every topic facet. Not offered: Digital Economy (nobody
        # carries it), Archived Topic, Unpublished Topic, Trade (staff only).
        # A topic outside any theme is still a topic.
        self.assertEqual([o['label'] for o in facet['options']], [
            'AI', 'Data Governance', 'India, China and Africa', 'Legacy Programme',
            'Privacy', 'Quantum'])
        self.assertEqual(facet['options'][0]['value'], self.ai_topic.pk)

    def test_topics_in_default_relation_unchanged(self):
        # Every other listing calls _topics_in(base): the curated `topics` field.
        expert = self.experts[11]
        expert.topics.set([self.trade])
        expert.save()
        base = PersonPage.objects.filter(pk=expert.pk)
        self.assertEqual(list(_topics_in(base)), [self.trade])
        self.assertEqual(list(_topics_in(base, 'derived_topics')), [])

    # --- filtering --------------------------------------------------------------

    def test_filter_by_theme(self):
        ai = self.ctx(theme=self.ai.pk)
        self.assertEqual(self.slugs(ai), self.expert_slugs(0, 1, 2, 3, 4, 5, 8))
        self.assertTrue(ai['router_has_filters'])
        self.assertEqual(self.checked(ai, 'theme'), ['AI and Transformative Technology'])
        self.assertEqual(self.checked(ai, 'topic'), [])
        # Options stay put while filtered (built from the unfiltered list).
        self.assertEqual(len(self.facet(ai, 'topic')['options']), 6)
        # OR within the facet; e08 carries both themes and is listed once.
        both = self.ctx(theme=[self.ai.pk, self.data.pk])
        self.assertEqual(self.slugs(both), self.expert_slugs(*range(9)))
        self.assertEqual(both['router_total'], 9)

    def test_filter_by_topic(self):
        quantum = self.ctx(topic=self.quantum.pk)
        self.assertEqual(self.slugs(quantum), self.expert_slugs(4, 5))
        self.assertTrue(quantum['router_has_filters'])
        self.assertEqual(self.checked(quantum, 'topic'), ['Quantum'])
        self.assertEqual(self.checked(quantum, 'theme'), [])
        either = self.ctx(topic=[self.ai_topic.pk, self.privacy.pk])
        self.assertEqual(self.slugs(either), self.expert_slugs(0, 1, 2, 3, 8))
        # An unmapped topic filters like any other.
        self.assertEqual(self.slugs(self.ctx(topic=self.unmapped.pk)), self.expert_slugs(10))

    def test_theme_and_topic_combine(self):
        # AND across facets — met by different topics: e08's Privacy is the Data
        # theme, its AI tag is the topic.
        self.assertEqual(self.slugs(self.ctx(theme=self.data.pk, topic=self.ai_topic.pk)),
                         self.expert_slugs(8))
        self.assertEqual(self.slugs(self.ctx(theme=self.ai.pk, topic=self.data_topic.pk)), [])
        self.assertEqual(
            self.slugs(self.ctx(theme=self.data.pk, topic=[self.ai_topic.pk, self.data_topic.pk])),
            self.expert_slugs(6, 7, 8))
        # Type too.
        self.assertEqual(
            self.slugs(self.ctx(type=self.senior.pk, theme=self.data.pk)), self.expert_slugs(6))
        self.assertEqual(
            self.slugs(self.ctx(type=self.senior.pk, topic=self.ai_topic.pk)),
            self.expert_slugs(0))

    def test_junk_values_filter_nothing(self):
        context = self.ctx(topic='abc', theme='x1')
        self.assertEqual(context['router_total'], 12)
        self.assertFalse(context['router_has_filters'])

    # --- old links --------------------------------------------------------------

    def test_old_theme_id_in_topic_param_filters_by_theme(self):
        old = self.ctx(topic=self.ai.pk)
        self.assertEqual(self.slugs(old), self.slugs(self.ctx(theme=self.ai.pk)))
        self.assertTrue(old['router_has_filters'])
        # Shown as the Theme it is, so its chip and checkbox are Theme's.
        self.assertEqual(self.checked(old, 'theme'), ['AI and Transformative Technology'])
        self.assertEqual(self.checked(old, 'topic'), [])
        # Clear All drops it with the rest of the listing's params.
        self.assertEqual(old['router_clear_url'], '/experts/')

    def test_old_theme_id_mixes_with_new_params(self):
        # A theme id beside a topic id in `experts-topic`: Theme AND Topic.
        self.assertEqual(self.slugs(self.ctx(topic=[self.data.pk, self.ai_topic.pk])),
                         self.expert_slugs(8))
        # Beside `experts-theme`: one Theme facet, OR'd.
        context = self.ctx(theme=self.data.pk, topic=self.ai.pk)
        self.assertEqual(context['router_total'], 9)
        self.assertEqual(self.checked(context, 'theme'),
                         ['AI and Transformative Technology', 'Data, Economy and Society'])
        # The same theme twice is still one selection.
        self.assertEqual(self.ctx(theme=self.ai.pk, topic=self.ai.pk)['router_total'], 7)

    def test_old_link_renders_theme_checked_with_its_chip(self):
        response = self.client.get('/experts/', {'experts-topic': self.ai.pk})
        self.assertContains(
            response, 'name="experts-theme" value="%s" checked' % self.ai.pk)
        self.assertNotContains(response, 'name="experts-topic" value="%s"' % self.ai.pk)
        chips = response.content.decode().split('data-router-facet="experts-theme"')[1]
        chips = chips.split('</ul>')[0]
        self.assertIn('data-chip-value="%s"' % self.ai.pk, chips)
        self.assertIn('AI and Transformative Technology', chips)
        self.assertContains(response, 'Showing 1–7 of 7')

    # --- rendering --------------------------------------------------------------

    def test_page_renders_theme_then_topic(self):
        response = self.client.get('/experts/')
        html = response.content.decode()
        labels = ['<summary class="ds-router__facet-label">%s</summary>' % label
                  for label in ('Type', 'Theme', 'Topic')]
        positions = [html.find(label) for label in labels]
        self.assertTrue(all(p > -1 for p in positions), positions)
        self.assertEqual(positions, sorted(positions))
        self.assertContains(response, 'name="experts-theme" value="%s"' % self.data.pk)
        self.assertContains(response, 'name="experts-topic" value="%s"' % self.quantum.pk)
        self.assertContains(response, 'data-router-facet="experts-theme"')
        self.assertContains(response, 'data-router-facet="experts-topic"')
        # Six topics: no search-within-facet yet.
        self.assertNotContains(response, 'data-router-facet-filter')

    def test_long_topic_list_gets_its_search_box(self):
        extra = [self.home.add_child(instance=TopicPage(
            title='Extra %02d' % i, slug='extra-%02d' % i, program_theme=self.ai))
            for i in range(5)]
        self.experts[11].derived_topics.set(extra)
        response = self.client.get('/experts/')
        self.assertContains(response, 'aria-label="Search Topic options"')
        self.assertNotContains(response, 'aria-label="Search Theme options"')

    # --- sparse data --------------------------------------------------------------

    def test_no_derived_topics_shows_every_expert_and_type_only(self):
        for expert in self.experts:
            expert.derived_topics.clear()
        context = self.ctx()
        self.assertEqual([f['key'] for f in context['router_facets']], ['type'])
        self.assertEqual(context['router_total'], 12)
        self.assertFalse(context['router_has_filters'])

    def test_one_theme_hides_theme_but_keeps_topic(self):
        for expert in self.experts:
            expert.derived_topics.set(
                [t for t in expert.derived_topics.all() if t.program_theme_id == self.ai.pk])
        context = self.ctx()
        self.assertEqual([f['key'] for f in context['router_facets']], ['type', 'topic'])
        self.assertEqual([o['label'] for o in self.facet(context, 'topic')['options']],
                         ['AI', 'Quantum'])

    def test_topic_facet_unauthored_builds_neither(self):
        context = self.ctx(self.listing(**dict(self.STAGING_LISTING, facets=['type'])))
        self.assertEqual([f['key'] for f in context['router_facets']], ['type'])

    # --- links into the listing ---------------------------------------------------

    def test_role_crumb_type_link_still_filters(self):
        # The #516 crumb deep-links `experts-type`; following it lists the role.
        crumb = person_hero_data(self.experts[0])['breadcrumb'][-1]
        self.assertEqual(crumb['title'], 'Senior Fellows')
        self.assertEqual(crumb['url'], '/experts/?experts-type=%s#router-experts'
                         % self.senior.pk)
        response = self.client.get(crumb['url'].split('#')[0])
        self.assertContains(response, 'name="experts-type" value="%s" checked' % self.senior.pk)
        self.assertContains(response, 'Showing 1–2 of 2')


class OtherPeopleListingsUnchangedTests(TestCase):
    """#521 changes the experts listing only: the person and staff listings'
    theme facet keeps the `topic` key and the Topic label (BugHerd #365/#440)."""

    @staticmethod
    def listing(**value):
        block = FacetedListingBlock()
        return block.get_prep_value(block.to_python(value))

    @classmethod
    def setUpTestData(cls):
        home = HomePage.objects.get()
        cls.people = home.add_child(instance=PeoplePage(title='People', slug='people'))
        cls.ai = home.add_child(instance=ThemePage(title='AI', slug='ai', accent='security'))
        cls.data = home.add_child(instance=ThemePage(title='Data', slug='data', accent='security'))
        cls.ai_topic = home.add_child(instance=TopicPage(
            title='AI topic', slug='ai-topic', program_theme=cls.ai))
        cls.data_topic = home.add_child(instance=TopicPage(
            title='Data topic', slug='data-topic', program_theme=cls.data))
        for i in range(12):
            for kind in ('Digital Policy Hub Fellow', 'Staff'):
                person = cls.people.add_child(instance=PersonPage(
                    title='%s %d' % (kind, i), slug='%s-%d' % (kind.lower().replace(' ', '-'), i),
                    last_name='M%d' % i))
                person.person_types.set([PersonType.objects.get(name=kind)])
                person.save()
                person.derived_topics.set([cls.ai_topic if i % 2 else cls.data_topic])

    def ctx(self, value, **params):
        request = RequestFactory().get('/', {'p-%s' % k: v for k, v in params.items()})
        return build_listing_context(request, value)

    def test_dph_fellow_listing_keeps_topic_as_themes(self):
        value = self.listing(card_type='person', person_type='', facets=['topic', 'type'],
                             prefix='p')
        context = self.ctx(value)
        self.assertEqual([(f['key'], f['label']) for f in context['router_facets']],
                         [('topic', 'Topic')])
        self.assertEqual([o['value'] for o in context['router_facets'][0]['options']],
                         [self.ai.pk, self.data.pk])
        # `p-topic` is still a theme id here.
        self.assertEqual(self.ctx(value, topic=self.ai.pk)['router_total'], 6)
        self.assertEqual(self.ctx(value, topic=self.ai_topic.pk)['router_total'], 0)

    def test_staff_listing_keeps_topic_as_themes(self):
        value = self.listing(card_type='staff', facets=['topic'], prefix='p')
        context = self.ctx(value)
        self.assertEqual([(f['key'], f['label']) for f in context['router_facets']],
                         [('topic', 'Topic'), ('letter', 'Last Name')])
        self.assertEqual(self.ctx(value, topic=self.data.pk)['router_total'], 6)

