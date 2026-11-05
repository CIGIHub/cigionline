import shutil
import tempfile

from core.models import BasicPage
from django.contrib.auth.models import User
from django.test import override_settings
from home.models import HomePage, Think7HomePage
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file
from wagtail.rich_text import RichText
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import nested_form_data

from .models import PeoplePage, PersonListPage, PersonPage, PersonType


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


class PersonPageDownloadsTests(WagtailPageTestCase):
    """The rail's High Resolution Photo download follows the Media photo field
    alone, whatever the person's type (BugHerd #526). Builds its own pages —
    no people.json fixture."""

    @classmethod
    def setUpClass(cls):
        # Uploaded test images go to a throwaway media root, not staticmedia/.
        media_root = tempfile.mkdtemp(prefix='people-tests-')
        cls.addClassCleanup(shutil.rmtree, media_root, ignore_errors=True)
        cls.enterClassContext(override_settings(MEDIA_ROOT=media_root))
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        home = HomePage.objects.get()
        cls.people = home.add_child(instance=PeoplePage(title='People', slug='people'))
        cls.image = get_image_model().objects.create(
            title='Media photo', file=get_test_image_file(filename='media.png'))

    def make_person(self, slug, types, image_media=None, bio=True):
        person = PersonPage(
            title=slug.replace('-', ' ').title(), slug=slug,
            image_media=image_media,
            body=[('paragraph', RichText('<p>A short biography.</p>'))] if bio else [],
        )
        self.people.add_child(instance=person)
        person.person_types.set(
            [PersonType.objects.get_or_create(name=name)[0] for name in types])
        person.save_revision().publish()
        return person

    def get(self, person):
        response = self.client.get(person.url)
        self.assertEqual(response.status_code, 200)
        return response

    def test_management_staff_with_media_photo_shows_download(self):
        # Dianna English's case: no Expert / Board Member / Media Contact type.
        person = self.make_person(
            'management-staff', ['Management Team', 'Staff'], self.image)
        response = self.get(person)
        self.assertContains(response, 'High Resolution Photo')
        self.assertContains(response, '<h2 class="ds-reading__aside-heading">Downloads</h2>', html=False)

    def test_expert_with_media_photo_shows_download(self):
        person = self.make_person('expert-person', ['Expert'], self.image)
        self.assertContains(self.get(person), 'High Resolution Photo')

    def test_no_media_photo_shows_no_download(self):
        person = self.make_person('no-photo', ['Expert'])
        response = self.get(person)
        self.assertNotContains(response, 'High Resolution Photo')
        self.assertNotContains(response, 'Downloads')
        # The bio still renders with its own column.
        self.assertContains(response, '<h2>Bio</h2>', html=False)

    def test_no_bio_staff_with_media_photo_shows_rail_alone(self):
        person = self.make_person('no-bio-staff', ['Staff'], self.image, bio=False)
        response = self.get(person)
        self.assertContains(response, 'High Resolution Photo')
        self.assertContains(response, 'ds-reading__aside')
        # No empty prose column, Bio heading or divider beside the rail.
        self.assertNotContains(response, '<h2>Bio</h2>', html=False)
        self.assertNotContains(response, 'ds-reading__main')
        self.assertNotContains(response, 'ds-reading__divider')

    def test_no_bio_no_media_photo_has_no_bio_band(self):
        person = self.make_person('no-bio-no-photo', ['Staff'], bio=False)
        response = self.get(person)
        self.assertNotContains(response, 'ds-reading--person')
        self.assertNotContains(response, 'High Resolution Photo')

    def test_no_bio_media_photo_keeps_dark_experts_rail(self):
        # The photo's light band now sits under the hero, so the tail rail
        # keeps its dark default instead of the no-sections light variant.
        person = self.make_person('no-bio-rail', ['Staff'], self.image, bio=False)
        self.assertEqual(self.get(person).context['experts_cfg']['surface'], 'dark')
        bare = self.make_person('no-bio-bare', ['Staff'], bio=False)
        self.assertEqual(self.get(bare).context['experts_cfg']['surface'], 'light')
