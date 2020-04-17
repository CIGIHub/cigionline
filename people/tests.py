from core.models import BasicPage, HomePage
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import nested_form_data, rich_text

from .models import PersonListPage, PersonPage


class PersonListPageTests(WagtailPageTests):
    def test_personlistpage_parent_page_types(self):
        """
        Verify allowed parent page types.
        """
        self.assertAllowedParentPageTypes(
            PersonListPage,
            {BasicPage, HomePage},
        )

    def test_personlistpage_child_page_types(self):
        """
        Verify allowed child page types.
        """
        self.assertAllowedSubpageTypes(
            PersonListPage,
            {PersonPage},
        )

    def test_can_create_under_homepage(self):
        """
        Test that a PersonListPage can be created as a child of a HomePage.
        """
        home_page = HomePage.objects.get()
        self.assertCanCreate(home_page, PersonListPage, nested_form_data({
            'title': 'People',
            'subtitle': rich_text('')
        }))


class PersonPageTests(WagtailPageTests):
    def test_personpage_parent_page_types(self):
        """
        Verify allowed parent page types.
        """
        self.assertAllowedParentPageTypes(
            PersonPage,
            {PersonListPage},
        )

    def test_personpage_child_page_types(self):
        """
        Verify allowed child page types.
        """
        self.assertAllowedSubpageTypes(
            PersonPage,
            {},
        )
