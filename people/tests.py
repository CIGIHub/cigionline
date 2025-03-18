from core.models import BasicPage
from django.contrib.auth.models import User
from home.models import HomePage, Think7HomePage
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import nested_form_data

from .models import PeoplePage, PersonListPage, PersonPage


class PeoplePageTests(WagtailPageTestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='testsuperuser',
            email='testsuperuser@example.com',
            password='testpassword'
        )
        self.client.login(username='testsuperuser', password='testpassword')

    def test_peoplepage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            PeoplePage,
            {HomePage, Think7HomePage},
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


class PersonListPageBasicTests(WagtailPageTestCase):
    fixtures = ["people.json"]

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='testsuperuser',
            email='testsuperuser@example.com',
            password='testpassword'
        )
        self.client.login(username='testsuperuser', password='testpassword')

    def test_personlistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            PersonListPage,
            {BasicPage, HomePage, Think7HomePage},
        )

    def test_personlistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            PersonListPage,
            {},
        )


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
