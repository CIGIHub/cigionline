from people.models import PeoplePage, PersonListPage
from research.models import TopicListPage
from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import nested_form_data

from .models import BasicPage, HomePage


class BasicPageTests(WagtailPageTests):
    def test_basicpage_parent_page_types(self):
        """
        Verify allowed parent page types.
        """
        self.assertAllowedParentPageTypes(
            BasicPage,
            {BasicPage, HomePage}
        )

    def test_basicpage_child_page_types(self):
        """
        Verify allowed child page types.
        """
        self.assertAllowedSubpageTypes(
            BasicPage,
            {BasicPage, PersonListPage}
        )


class HomePageTests(WagtailPageTests):
    def test_homepage_child_page_types(self):
        """
        Verify allowed child page types.
        """
        self.assertAllowedSubpageTypes(
            HomePage,
            {BasicPage, PeoplePage, PersonListPage, TopicListPage}
        )

    def test_cannot_create_homepage(self):
        """
        Test that we can't create a second home page. Wagtail will create a home
        page object on initialization so we don't need to create one first.
        """
        root_page = Page.objects.get(pk=1)
        try:
            self.assertCanCreate(root_page, HomePage, nested_form_data({
                'title': 'Home',
            }))
            self.fail('Expected to error')
        except AssertionError:
            pass
