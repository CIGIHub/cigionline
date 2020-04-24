from core.models import HomePage
from django.template import Context, Template
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import nested_form_data

from .models import TopicListPage, TopicPage


class TopicListPageTests(WagtailPageTests):
    def test_topiclistpage_parent_page_types(self):
        """
        Verify allowed parent page types.
        """
        self.assertAllowedParentPageTypes(
            TopicListPage,
            {HomePage},
        )

    def test_topiclistpage_child_page_types(self):
        """
        Verify allowed child page types.
        """
        self.assertAllowedSubpageTypes(
            TopicListPage,
            {TopicPage},
        )

    def test_can_create_under_homepage(self):
        """
        Test that a TopicListPage can be created as a child of a HomePage.
        """
        home_page = HomePage.objects.get()
        self.assertCanCreate(home_page, TopicListPage, nested_form_data({
            'title': 'Topics',
        }))

    def test_cannot_create_second_topiclistpage(self):
        """
        Test that a TopicListPage cannot be created if a TopicListPage already
        exists.
        """
        home_page = HomePage.objects.get()
        # Create the first TopicListPage
        self.assertCanCreate(home_page, TopicListPage, nested_form_data({
            'title': 'Topics',
        }))
        try:
            self.assertCanCreate(home_page, TopicListPage, nested_form_data({
                'title': 'Topics 2',
            }))
            self.fail('Expected to error')
        except AssertionError as ae:
            if str(ae) == 'Creating a research.topiclistpage returned a 403':
                pass
            else:
                raise ae


class TopicPageTests(WagtailPageTests):
    def test_topicpage_parent_page_types(self):
        """
        Verify allowed parent page types.
        """
        self.assertAllowedParentPageTypes(
            TopicPage,
            {TopicListPage},
        )

    def test_topicpage_child_page_types(self):
        """
        Verify allowed child page types.
        """
        self.assertAllowedSubpageTypes(
            TopicPage,
            {},
        )


class HighlightedTopicsTests(WagtailPageTests):
    TEMPLATE = Template("{% load topic_tags %} {% highlighted_topics %}")

    def setUp(self):
        for n in range(5):
            TopicPage.objects.create(path="/test{0}".format(n), depth=1, title="test{0}".format(n), slug="test{0}".format(n), archive=0, live=True)

    def test_topics_show_up(self):
        rendered = self.TEMPLATE.render(Context({}))
        self.assertIn("test4", rendered)
        self.assertNotIn("test5", rendered)

    def test_topics_not_live_do_not_show_up(self):
        TopicPage.objects.create(path="/test6", depth=1, title="test6", slug="test6", archive=0, live=False)
        topic1 = TopicPage.objects.get(title="test1")

        rendered = self.TEMPLATE.render(Context({}))
        self.assertIn("test1", rendered)
        self.assertNotIn("test6", rendered)

        # See if topic disappears after unpublishing
        setattr(topic1, 'live', False)
        topic1.save()
        rendered = self.TEMPLATE.render(Context({}))
        self.assertNotIn("test1", rendered)
