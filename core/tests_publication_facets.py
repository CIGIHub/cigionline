from django.test import RequestFactory, TestCase
from django.utils import timezone

from home.models import HomePage
from publications.models import PublicationPage, PublicationTypePage

from .faceted_listing import build_listing_context, default_listing_prefix


class PublicationFacetedListingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        home = HomePage.objects.get()
        cls.working_paper = home.add_child(instance=PublicationTypePage(
            title='Working Paper', slug='working-paper'))
        cls.policy_brief = home.add_child(instance=PublicationTypePage(
            title='Policy Briefs', slug='publication-facet-policy-briefs'))
        cls.book = home.add_child(instance=PublicationTypePage(
            title='Books', slug='publication-facet-books'))
        cls.publications = {}
        for publication_type in (cls.working_paper, cls.policy_brief, cls.book):
            page = home.add_child(instance=PublicationPage(
                title='%s result' % publication_type.title,
                slug='publication-facet-%s' % publication_type.slug,
                publication_type=publication_type,
                publishing_date=timezone.now()))
            cls.publications[publication_type.pk] = page

    def context(self, value, params=None):
        request = RequestFactory().get('/', params or {})
        return build_listing_context(request, {
            'card_type': 'publication',
            'prefix': 'pubs',
            'show_filters': True,
            'show_search': True,
            'facets': ['type'],
            **value,
        })

    def result_ids(self, context):
        return {page.pk for page in context['router_results']}

    def test_existing_single_type_scope_is_unchanged(self):
        context = self.context({'publication_type': 'working-paper'})
        self.assertEqual(
            self.result_ids(context), {self.publications[self.working_paper.pk].pk})

    def test_all_types_and_type_filter(self):
        value = {'publication_scope': 'all'}
        context = self.context(value)
        self.assertTrue(context['router_show_filters'])
        self.assertEqual(self.result_ids(context), {
            page.pk for page in self.publications.values()})
        facet = context['router_facets'][0]
        self.assertEqual(facet['key'], 'type')
        self.assertEqual(
            [option['label'] for option in facet['options']],
            ['Books', 'Policy Briefs', 'Working Paper'])

        filtered = self.context(value, {'pubs-type': self.book.pk})
        self.assertEqual(
            self.result_ids(filtered), {self.publications[self.book.pk].pk})
        self.assertTrue(next(
            option for option in filtered['router_facets'][0]['options']
            if option['value'] == self.book.pk)['checked'])

    def test_include_and_exclude_selected_types(self):
        selected = [self.working_paper, self.policy_brief]
        included = self.context({
            'publication_scope': 'include', 'publication_types': selected})
        self.assertEqual(self.result_ids(included), {
            self.publications[self.working_paper.pk].pk,
            self.publications[self.policy_brief.pk].pk,
        })
        excluded = self.context({
            'publication_scope': 'exclude', 'publication_types': selected})
        self.assertEqual(
            self.result_ids(excluded), {self.publications[self.book.pk].pk})
        self.assertEqual(
            [option['label'] for option in excluded['router_facets'][0]['options']],
            ['Books'])

    def test_selected_types_make_default_prefix_distinct(self):
        base = {'card_type': 'publication', 'publication_scope': 'include'}
        self.assertNotEqual(
            default_listing_prefix({**base, 'publication_types': [self.book]}),
            default_listing_prefix({**base, 'publication_types': [self.policy_brief]}))

    def test_single_mode_keeps_existing_default_prefix(self):
        value = {'card_type': 'publication', 'publication_type': 'working-paper'}
        self.assertEqual(
            default_listing_prefix(value),
            default_listing_prefix({**value, 'publication_scope': 'single'}))
