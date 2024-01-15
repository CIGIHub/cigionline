from core.models import BasicPage
from home.models import HomePage
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import nested_form_data, rich_text

from .models import PeoplePage, PersonListPage, PersonPage


class PeoplePageTests(WagtailPageTestCase):
    def test_peoplepage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            PeoplePage,
            {HomePage},
        )

    def test_people_page_child_page_types(self):
        self.assertAllowedSubpageTypes(
            PeoplePage,
            {PersonPage},
        )

    def test_can_create_under_homepage(self):
        home_page = HomePage.objects.get()
        self.assertCanCreate(home_page, PeoplePage, nested_form_data({
            'title': 'People',
        }))

    def test_cannot_create_second_peoplepage(self):
        home_page = HomePage.objects.get()
        self.assertCanCreate(home_page, PeoplePage, nested_form_data({
            'title': 'People',
        }))
        try:
            self.assertCanCreate(home_page, PeoplePage, nested_form_data({
                'title': 'People 2',
            }))
            self.fail('Expected to error')
        except AssertionError as ae:
            if str(ae) == "Creating a page people.peoplepage didn't redirect the user to the explorer, but to [(\'/admin/\', 302)]":
                pass
            else:
                raise ae


class PersonListPageBasicTests(WagtailPageTestCase):
    fixtures = ["people.json"]

    def test_personlistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            PersonListPage,
            {BasicPage, HomePage},
        )

    def test_personlistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            PersonListPage,
            {},
        )

    def test_cannot_create_fourth_personlistpage(self):
        home_page = HomePage.objects.get()
        try:
            self.assertCanCreate(home_page, PersonListPage, nested_form_data({
                'title': 'Person List Page',
                'subtitle': rich_text(''),
            }))
            self.fail('Expected to error')
        except AssertionError as ae:
            if str(ae) == "Creating a page people.personlistpage didn't redirect the user to the explorer, but to [(\'/admin/\', 302)]":
                pass
            else:
                raise ae


class PersonListPageRequestTests(WagtailPageTestCase):
    fixtures = ["people.json"]

    def setUp(self):
        home_page = HomePage.objects.get()
        home_page.numchild = 4
        home_page.save()

    def test_experts_page_returns_200(self):
        response = self.client.get('/experts/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'people/person_list_experts_page.html')

    def test_staff_page_returns_200(self):
        response = self.client.get('/staff/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'people/person_list_staff_page.html')

    def test_leadership_page_returns_200(self):
        response = self.client.get('/leadership/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'people/person_list_leadership_page.html')

    def test_leadership_page_board_members(self):
        response = self.client.get('/leadership/')
        board_member_live = PersonPage.objects.get(title='Board Member Live')
        self.assertEqual(list(response.context['board_members']), [board_member_live])

    def test_leadership_page_senior_management(self):
        response = self.client.get('/leadership/?show=senior-management')
        management_team_live = PersonPage.objects.get(title='Management Team Live')
        self.assertEqual(list(response.context['senior_management']), [management_team_live])


class PersonPageTests(WagtailPageTestCase):
    fixtures = ["people.json"]

    def test_personpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            PersonPage,
            {PeoplePage},
        )

    def test_personpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            PersonPage,
            {},
        )
