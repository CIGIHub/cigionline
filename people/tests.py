from home.models import HomePage
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import nested_form_data

from .models import PersonListPage, PersonPage


class PersonListPageTests(WagtailPageTests):
    def test_personlistpage_parent_page_types(self):
        """
        Verify allowed parent page types.
        """
        self.assertAllowedParentPageTypes(
            PersonListPage,
            {HomePage},
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
        }))

    def test_cannot_create_second_personlistpage(self):
        """
        Test that a PersonListPage cannot be created if a PersonListPage already
        exists.
        """
        home_page = HomePage.objects.get()
        # Create the first PersonListPage
        self.assertCanCreate(home_page, PersonListPage, nested_form_data({
            'title': 'People',
        }))
        try:
            self.assertCanCreate(home_page, PersonListPage, nested_form_data({
                'title': 'People 2',
            }))
            self.fail('Expected to error')
        except AssertionError as ae:
            if str(ae) == 'Creating a people.personlistpage returned a 403':
                pass
            else:
                raise ae


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
