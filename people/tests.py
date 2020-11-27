from core.models import BasicPage, HomePage
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import nested_form_data, rich_text

from .models import PeoplePage, PersonListPage, PersonPage


class PeoplePageTests(WagtailPageTests):
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
            if str(ae) == 'Creating a page people.peoplepage didnt redirect the user to the explorer, but to [(\'/admin/\', 302)]':
                pass
            else:
                raise ae


class PersonListPageBasicTests(WagtailPageTests):
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
            if str(ae) == 'Creating a page people.personlistpage didnt redirect the user to the explorer, but to [(\'/admin/\', 302)]':
                pass
            else:
                raise ae


class PersonListPageRequestTests(WagtailPageTests):
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

    def test_experts_page_should_not_show_live_board_member(self):
        response = self.client.get('/experts/')
        board_member_live = PersonPage.objects.get(title='Board Member Live')
        self.assertNotIn(board_member_live, response.context['people'])

    def test_experts_page_should_not_show_archived_board_member(self):
        response = self.client.get('/experts/')
        board_member_archived = PersonPage.objects.get(title='Board Member Archived')
        self.assertNotIn(board_member_archived, response.context['people'])

    def test_experts_page_should_not_show_draft_board_member(self):
        response = self.client.get('/experts/')
        board_member_draft = PersonPage.objects.get(title='Board Member Draft')
        self.assertNotIn(board_member_draft, response.context['people'])

    def test_experts_page_should_show_live_cigi_chair(self):
        response = self.client.get('/experts/')
        cigi_chair_live = PersonPage.objects.get(title='CIGI Chair Live')
        self.assertIn(cigi_chair_live, response.context['people'])

    def test_experts_page_should_not_show_archived_cigi_chair(self):
        response = self.client.get('/experts/')
        cigi_chair_archived = PersonPage.objects.get(title='CIGI Chair Archived')
        self.assertNotIn(cigi_chair_archived, response.context['people'])

    def test_experts_page_should_not_show_draft_cigi_chair(self):
        response = self.client.get('/experts/')
        cigi_chair_draft = PersonPage.objects.get(title='CIGI Chair Draft')
        self.assertNotIn(cigi_chair_draft, response.context['people'])

    def test_experts_page_should_not_should_live_commission(self):
        response = self.client.get('/experts/')
        commission_live = PersonPage.objects.get(title='Commission Live')
        self.assertNotIn(commission_live, response.context['people'])

    def test_experts_page_should_not_should_archived_commission(self):
        response = self.client.get('/experts/')
        commission_archived = PersonPage.objects.get(title='Commission Archived')
        self.assertNotIn(commission_archived, response.context['people'])

    def test_experts_page_should_not_should_draft_commission(self):
        response = self.client.get('/experts/')
        commission_draft = PersonPage.objects.get(title='Commission Draft')
        self.assertNotIn(commission_draft, response.context['people'])

    def test_experts_page_should_show_live_expert(self):
        response = self.client.get('/experts/')
        expert_live = PersonPage.objects.get(title='Expert Live')
        self.assertIn(expert_live, response.context['people'])

    def test_experts_page_should_not_show_archived_expert(self):
        response = self.client.get('/experts/')
        expert_archived = PersonPage.objects.get(title='Expert Archived')
        self.assertNotIn(expert_archived, response.context['people'])

    def test_experts_page_should_not_show_draft_expert(self):
        response = self.client.get('/experts/')
        expert_draft = PersonPage.objects.get(title='Expert Draft')
        self.assertNotIn(expert_draft, response.context['people'])

    def test_experts_page_should_not_show_live_external_profile(self):
        response = self.client.get('/experts/')
        external_profile_live = PersonPage.objects.get(title='External profile Live')
        self.assertNotIn(external_profile_live, response.context['people'])

    def test_experts_page_should_not_show_archived_external_profile(self):
        response = self.client.get('/experts/')
        external_profile_archived = PersonPage.objects.get(title='External profile Archived')
        self.assertNotIn(external_profile_archived, response.context['people'])

    def test_experts_page_should_not_show_draft_external_profile(self):
        response = self.client.get('/experts/')
        external_profile_draft = PersonPage.objects.get(title='External profile Draft')
        self.assertNotIn(external_profile_draft, response.context['people'])

    def test_experts_page_should_not_show_live_g20_expert(self):
        response = self.client.get('/experts/')
        g20_expert_live = PersonPage.objects.get(title='G20 Expert Live')
        self.assertNotIn(g20_expert_live, response.context['people'])

    def test_experts_page_should_not_show_archived_g20_expert(self):
        response = self.client.get('/experts/')
        g20_expert_archived = PersonPage.objects.get(title='G20 Expert Archived')
        self.assertNotIn(g20_expert_archived, response.context['people'])

    def test_experts_page_should_not_show_draft_g20_expert(self):
        response = self.client.get('/experts/')
        g20_expert_draft = PersonPage.objects.get(title='G20 Expert Draft')
        self.assertNotIn(g20_expert_draft, response.context['people'])

    def test_experts_page_should_not_show_live_management_team(self):
        response = self.client.get('/experts/')
        management_team_live = PersonPage.objects.get(title='Management Team Live')
        self.assertNotIn(management_team_live, response.context['people'])

    def test_experts_page_should_not_show_archived_management_team(self):
        response = self.client.get('/experts/')
        management_team_archived = PersonPage.objects.get(title='Management Team Archived')
        self.assertNotIn(management_team_archived, response.context['people'])

    def test_experts_page_should_not_show_draft_management_team(self):
        response = self.client.get('/experts/')
        management_team_draft = PersonPage.objects.get(title='Management Team Draft')
        self.assertNotIn(management_team_draft, response.context['people'])

    def test_experts_page_should_not_show_live_media_contact(self):
        response = self.client.get('/experts/')
        media_contact_live = PersonPage.objects.get(title='Media Contact Live')
        self.assertNotIn(media_contact_live, response.context['people'])

    def test_experts_page_should_not_show_archived_media_contact(self):
        response = self.client.get('/experts/')
        media_contact_archived = PersonPage.objects.get(title='Media Contact Archived')
        self.assertNotIn(media_contact_archived, response.context['people'])

    def test_experts_page_should_not_show_draft_media_contact(self):
        response = self.client.get('/experts/')
        media_contact_draft = PersonPage.objects.get(title='Media Contact Draft')
        self.assertNotIn(media_contact_draft, response.context['people'])

    def test_experts_page_should_not_show_live_person(self):
        response = self.client.get('/experts/')
        person_live = PersonPage.objects.get(title='Person Live')
        self.assertNotIn(person_live, response.context['people'])

    def test_experts_page_should_not_show_archived_person(self):
        response = self.client.get('/experts/')
        person_archived = PersonPage.objects.get(title='Person Archived')
        self.assertNotIn(person_archived, response.context['people'])

    def test_experts_page_should_not_show_draft_person(self):
        response = self.client.get('/experts/')
        person_draft = PersonPage.objects.get(title='Person Draft')
        self.assertNotIn(person_draft, response.context['people'])

    def test_experts_page_should_not_show_live_program_director(self):
        response = self.client.get('/experts/')
        program_director_live = PersonPage.objects.get(title='Program Director Live')
        self.assertNotIn(program_director_live, response.context['people'])

    def test_experts_page_should_not_show_archived_program_director(self):
        response = self.client.get('/experts/')
        program_director_archived = PersonPage.objects.get(title='Program Director Archived')
        self.assertNotIn(program_director_archived, response.context['people'])

    def test_experts_page_should_not_show_draft_program_director(self):
        response = self.client.get('/experts/')
        program_director_draft = PersonPage.objects.get(title='Program Director Draft')
        self.assertNotIn(program_director_draft, response.context['people'])

    def test_experts_page_should_not_show_live_program_manager(self):
        response = self.client.get('/experts/')
        program_manager_live = PersonPage.objects.get(title='Program Manager Live')
        self.assertNotIn(program_manager_live, response.context['people'])

    def test_experts_page_should_not_show_archived_program_manager(self):
        response = self.client.get('/experts/')
        program_manager_archived = PersonPage.objects.get(title='Program Manager Archived')
        self.assertNotIn(program_manager_archived, response.context['people'])

    def test_experts_page_should_not_show_draft_program_manager(self):
        response = self.client.get('/experts/')
        program_manager_draft = PersonPage.objects.get(title='Program Manager Draft')
        self.assertNotIn(program_manager_draft, response.context['people'])

    def test_experts_page_should_not_show_live_research_advisor(self):
        response = self.client.get('/experts/')
        research_advisor_live = PersonPage.objects.get(title='Research Advisor Live')
        self.assertNotIn(research_advisor_live, response.context['people'])

    def test_experts_page_should_not_show_archived_research_advisor(self):
        response = self.client.get('/experts/')
        research_advisor_archived = PersonPage.objects.get(title='Research Advisor Archived')
        self.assertNotIn(research_advisor_archived, response.context['people'])

    def test_experts_page_should_not_show_draft_research_advisor(self):
        response = self.client.get('/experts/')
        research_advisor_draft = PersonPage.objects.get(title='Research Advisor Draft')
        self.assertNotIn(research_advisor_draft, response.context['people'])

    def test_experts_page_should_not_show_live_research_associate(self):
        response = self.client.get('/experts/')
        research_associate_live = PersonPage.objects.get(title='Research Associate Live')
        self.assertNotIn(research_associate_live, response.context['people'])

    def test_experts_page_should_not_show_archived_research_associate(self):
        response = self.client.get('/experts/')
        research_associate_archived = PersonPage.objects.get(title='Research Associate Archived')
        self.assertNotIn(research_associate_archived, response.context['people'])

    def test_experts_page_should_not_show_draft_research_associate(self):
        response = self.client.get('/experts/')
        research_associate_draft = PersonPage.objects.get(title='Research Associate Draft')
        self.assertNotIn(research_associate_draft, response.context['people'])

    def test_experts_page_should_not_show_live_research_fellow(self):
        response = self.client.get('/experts/')
        research_fellow_live = PersonPage.objects.get(title='Research Fellow Live')
        self.assertNotIn(research_fellow_live, response.context['people'])

    def test_experts_page_should_not_show_archived_research_fellow(self):
        response = self.client.get('/experts/')
        research_fellow_archived = PersonPage.objects.get(title='Research Fellow Archived')
        self.assertNotIn(research_fellow_archived, response.context['people'])

    def test_experts_page_should_not_show_draft_research_fellow(self):
        response = self.client.get('/experts/')
        research_fellow_draft = PersonPage.objects.get(title='Research Fellow Draft')
        self.assertNotIn(research_fellow_draft, response.context['people'])

    def test_experts_page_should_not_show_live_speaker(self):
        response = self.client.get('/experts/')
        speaker_live = PersonPage.objects.get(title='Speaker Live')
        self.assertNotIn(speaker_live, response.context['people'])

    def test_experts_page_should_not_show_archived_speaker(self):
        response = self.client.get('/experts/')
        speaker_archived = PersonPage.objects.get(title='Speaker Archived')
        self.assertNotIn(speaker_archived, response.context['people'])

    def test_experts_page_should_not_show_draft_speaker(self):
        response = self.client.get('/experts/')
        speaker_draft = PersonPage.objects.get(title='Speaker Draft')
        self.assertNotIn(speaker_draft, response.context['people'])

    def test_experts_page_should_not_show_live_staff(self):
        response = self.client.get('/experts/')
        staff_live = PersonPage.objects.get(title='Staff Live')
        self.assertNotIn(staff_live, response.context['people'])

    def test_experts_page_should_not_show_archived_staff(self):
        response = self.client.get('/experts/')
        staff_archived = PersonPage.objects.get(title='Staff Archived')
        self.assertNotIn(staff_archived, response.context['people'])

    def test_experts_page_should_not_show_draft_staff(self):
        response = self.client.get('/experts/')
        staff_draft = PersonPage.objects.get(title='Staff Draft')
        self.assertNotIn(staff_draft, response.context['people'])

    def test_experts_page_order_accent_insensitive(self):
        response = self.client.get('/experts/')
        expert_pages = list(response.context['people'])
        kimi_raikkonen = PersonPage.objects.get(title='Kimi Räikkönen')
        daniel_ricciardo = PersonPage.objects.get(title='Daniel Ricciardo')
        self.assertIn(kimi_raikkonen, expert_pages)
        self.assertIn(daniel_ricciardo, expert_pages)
        self.assertLess(
            expert_pages.index(kimi_raikkonen),
            expert_pages.index(daniel_ricciardo),
        )

    def test_staff_directory_page_should_not_show_live_board_member(self):
        response = self.client.get('/staff/')
        board_member_live = PersonPage.objects.get(title='Board Member Live')
        self.assertNotIn(board_member_live, response.context['people'])

    def test_staff_directory_page_should_not_show_archived_board_member(self):
        response = self.client.get('/staff/')
        board_member_archived = PersonPage.objects.get(title='Board Member Archived')
        self.assertNotIn(board_member_archived, response.context['people'])

    def test_staff_directory_page_should_not_show_draft_board_member(self):
        response = self.client.get('/staff/')
        board_member_draft = PersonPage.objects.get(title='Board Member Draft')
        self.assertNotIn(board_member_draft, response.context['people'])

    def test_staff_directory_page_should_not_show_live_cigi_chair(self):
        response = self.client.get('/staff/')
        cigi_chair_live = PersonPage.objects.get(title='CIGI Chair Live')
        self.assertNotIn(cigi_chair_live, response.context['people'])

    def test_staff_directory_page_should_not_show_archived_cigi_chair(self):
        response = self.client.get('/staff/')
        cigi_chair_archived = PersonPage.objects.get(title='CIGI Chair Archived')
        self.assertNotIn(cigi_chair_archived, response.context['people'])

    def test_staff_directory_page_should_not_show_draft_cigi_chair(self):
        response = self.client.get('/staff/')
        cigi_chair_draft = PersonPage.objects.get(title='CIGI Chair Draft')
        self.assertNotIn(cigi_chair_draft, response.context['people'])

    def test_staff_directory_page_should_not_show_live_commission(self):
        response = self.client.get('/staff/')
        commission_live = PersonPage.objects.get(title='Commission Live')
        self.assertNotIn(commission_live, response.context['people'])

    def test_staff_directory_page_should_not_show_archived_commission(self):
        response = self.client.get('/staff/')
        commission_archived = PersonPage.objects.get(title='Commission Archived')
        self.assertNotIn(commission_archived, response.context['people'])

    def test_staff_directory_page_should_not_show_draft_commission(self):
        response = self.client.get('/staff/')
        commission_draft = PersonPage.objects.get(title='Commission Draft')
        self.assertNotIn(commission_draft, response.context['people'])

    def test_staff_directory_page_should_not_show_live_expert(self):
        response = self.client.get('/staff/')
        expert_live = PersonPage.objects.get(title='Expert Live')
        self.assertNotIn(expert_live, response.context['people'])

    def test_staff_directory_page_should_not_show_archived_expert(self):
        response = self.client.get('/staff/')
        expert_archived = PersonPage.objects.get(title='Expert Archived')
        self.assertNotIn(expert_archived, response.context['people'])

    def test_staff_directory_page_should_not_show_draft_expert(self):
        response = self.client.get('/staff/')
        expert_draft = PersonPage.objects.get(title='Expert Draft')
        self.assertNotIn(expert_draft, response.context['people'])

    def test_staff_directory_page_should_not_show_live_external_profile(self):
        response = self.client.get('/staff/')
        external_profile_live = PersonPage.objects.get(title='External profile Live')
        self.assertNotIn(external_profile_live, response.context['people'])

    def test_staff_directory_page_should_not_show_archived_external_profile(self):
        response = self.client.get('/staff/')
        external_profile_archived = PersonPage.objects.get(title='External profile Archived')
        self.assertNotIn(external_profile_archived, response.context['people'])

    def test_staff_directory_page_should_not_show_draft_external_profile(self):
        response = self.client.get('/staff/')
        external_profile_draft = PersonPage.objects.get(title='External profile Draft')
        self.assertNotIn(external_profile_draft, response.context['people'])

    def test_staff_directory_page_should_not_show_live_g20_expert(self):
        response = self.client.get('/staff/')
        g20_expert_live = PersonPage.objects.get(title='G20 Expert Live')
        self.assertNotIn(g20_expert_live, response.context['people'])

    def test_staff_directory_page_should_not_show_archived_g20_expert(self):
        response = self.client.get('/staff/')
        g20_expert_archived = PersonPage.objects.get(title='G20 Expert Archived')
        self.assertNotIn(g20_expert_archived, response.context['people'])

    def test_staff_directory_page_should_not_show_draft_g20_expert(self):
        response = self.client.get('/staff/')
        g20_expert_draft = PersonPage.objects.get(title='G20 Expert Draft')
        self.assertNotIn(g20_expert_draft, response.context['people'])

    def test_staff_directory_page_should_not_show_live_management_team(self):
        response = self.client.get('/staff/')
        management_team_live = PersonPage.objects.get(title='Management Team Live')
        self.assertNotIn(management_team_live, response.context['people'])

    def test_staff_directory_page_should_not_show_archived_management_team(self):
        response = self.client.get('/staff/')
        management_team_archived = PersonPage.objects.get(title='Management Team Archived')
        self.assertNotIn(management_team_archived, response.context['people'])

    def test_staff_directory_page_should_not_show_draft_management_team(self):
        response = self.client.get('/staff/')
        management_team_draft = PersonPage.objects.get(title='Management Team Draft')
        self.assertNotIn(management_team_draft, response.context['people'])

    def test_staff_directory_page_should_not_show_live_media_contact(self):
        response = self.client.get('/staff/')
        media_contact_live = PersonPage.objects.get(title='Media Contact Live')
        self.assertNotIn(media_contact_live, response.context['people'])

    def test_staff_directory_page_should_not_show_archived_media_contact(self):
        response = self.client.get('/staff/')
        media_contact_archived = PersonPage.objects.get(title='Media Contact Archived')
        self.assertNotIn(media_contact_archived, response.context['people'])

    def test_staff_directory_page_should_not_show_draft_media_contact(self):
        response = self.client.get('/staff/')
        media_contact_draft = PersonPage.objects.get(title='Media Contact Draft')
        self.assertNotIn(media_contact_draft, response.context['people'])

    def test_staff_directory_page_should_not_show_live_person(self):
        response = self.client.get('/staff/')
        person_live = PersonPage.objects.get(title='Person Live')
        self.assertNotIn(person_live, response.context['people'])

    def test_staff_directory_page_should_not_show_archived_person(self):
        response = self.client.get('/staff/')
        person_archived = PersonPage.objects.get(title='Person Archived')
        self.assertNotIn(person_archived, response.context['people'])

    def test_staff_directory_page_should_not_show_draft_person(self):
        response = self.client.get('/staff/')
        person_draft = PersonPage.objects.get(title='Person Draft')
        self.assertNotIn(person_draft, response.context['people'])

    def test_staff_directory_page_should_not_show_live_program_director(self):
        response = self.client.get('/staff/')
        program_director_live = PersonPage.objects.get(title='Program Director Live')
        self.assertNotIn(program_director_live, response.context['people'])

    def test_staff_directory_page_should_not_show_archived_program_director(self):
        response = self.client.get('/staff/')
        program_director_archived = PersonPage.objects.get(title='Program Director Archived')
        self.assertNotIn(program_director_archived, response.context['people'])

    def test_staff_directory_page_should_not_show_draft_program_director(self):
        response = self.client.get('/staff/')
        program_director_draft = PersonPage.objects.get(title='Program Director Draft')
        self.assertNotIn(program_director_draft, response.context['people'])

    def test_staff_directory_page_should_not_show_live_program_manager(self):
        response = self.client.get('/staff/')
        program_manager_live = PersonPage.objects.get(title='Program Manager Live')
        self.assertNotIn(program_manager_live, response.context['people'])

    def test_staff_directory_page_should_not_show_archived_program_manager(self):
        response = self.client.get('/staff/')
        program_manager_archived = PersonPage.objects.get(title='Program Manager Archived')
        self.assertNotIn(program_manager_archived, response.context['people'])

    def test_staff_directory_page_should_not_show_draft_program_manager(self):
        response = self.client.get('/staff/')
        program_manager_draft = PersonPage.objects.get(title='Program Manager Draft')
        self.assertNotIn(program_manager_draft, response.context['people'])

    def test_staff_directory_page_should_not_show_live_research_advisor(self):
        response = self.client.get('/staff/')
        research_advisor_live = PersonPage.objects.get(title='Research Advisor Live')
        self.assertNotIn(research_advisor_live, response.context['people'])

    def test_staff_directory_page_should_not_show_archived_research_advisor(self):
        response = self.client.get('/staff/')
        research_advisor_archived = PersonPage.objects.get(title='Research Advisor Archived')
        self.assertNotIn(research_advisor_archived, response.context['people'])

    def test_staff_directory_page_should_not_show_draft_research_advisor(self):
        response = self.client.get('/staff/')
        research_advisor_draft = PersonPage.objects.get(title='Research Advisor Draft')
        self.assertNotIn(research_advisor_draft, response.context['people'])

    def test_staff_directory_page_should_not_show_live_research_associate(self):
        response = self.client.get('/staff/')
        research_associate_live = PersonPage.objects.get(title='Research Associate Live')
        self.assertNotIn(research_associate_live, response.context['people'])

    def test_staff_directory_page_should_not_show_archived_research_associate(self):
        response = self.client.get('/staff/')
        research_associate_archived = PersonPage.objects.get(title='Research Associate Archived')
        self.assertNotIn(research_associate_archived, response.context['people'])

    def test_staff_directory_page_should_not_show_draft_research_associate(self):
        response = self.client.get('/staff/')
        research_associate_draft = PersonPage.objects.get(title='Research Associate Draft')
        self.assertNotIn(research_associate_draft, response.context['people'])

    def test_staff_directory_page_should_not_show_live_research_fellow(self):
        response = self.client.get('/staff/')
        research_fellow_live = PersonPage.objects.get(title='Research Fellow Live')
        self.assertNotIn(research_fellow_live, response.context['people'])

    def test_staff_directory_page_should_not_show_archived_research_fellow(self):
        response = self.client.get('/staff/')
        research_fellow_archived = PersonPage.objects.get(title='Research Fellow Archived')
        self.assertNotIn(research_fellow_archived, response.context['people'])

    def test_staff_directory_page_should_not_show_draft_research_fellow(self):
        response = self.client.get('/staff/')
        research_fellow_draft = PersonPage.objects.get(title='Research Fellow Draft')
        self.assertNotIn(research_fellow_draft, response.context['people'])

    def test_staff_directory_page_should_not_show_live_speaker(self):
        response = self.client.get('/staff/')
        speaker_live = PersonPage.objects.get(title='Speaker Live')
        self.assertNotIn(speaker_live, response.context['people'])

    def test_staff_directory_page_should_not_show_archived_speaker(self):
        response = self.client.get('/staff/')
        speaker_archived = PersonPage.objects.get(title='Speaker Archived')
        self.assertNotIn(speaker_archived, response.context['people'])

    def test_staff_directory_page_should_not_show_draft_speaker(self):
        response = self.client.get('/staff/')
        speaker_draft = PersonPage.objects.get(title='Speaker Draft')
        self.assertNotIn(speaker_draft, response.context['people'])

    def test_staff_directory_page_should_show_live_staff(self):
        response = self.client.get('/staff/')
        staff_live = PersonPage.objects.get(title='Staff Live')
        self.assertIn(staff_live, response.context['people'])

    def test_staff_directory_page_should_not_show_archived_staff(self):
        response = self.client.get('/staff/')
        staff_archived = PersonPage.objects.get(title='Staff Archived')
        self.assertNotIn(staff_archived, response.context['people'])

    def test_staff_directory_page_should_not_show_draft_staff(self):
        response = self.client.get('/staff/')
        staff_draft = PersonPage.objects.get(title='Staff Draft')
        self.assertNotIn(staff_draft, response.context['people'])

    def test_staff_directory_page_order_accent_insensitive(self):
        response = self.client.get('/staff/')
        staff_pages = list(response.context['people'])
        kimi_raikkonen = PersonPage.objects.get(title='Kimi Räikkönen')
        daniel_ricciardo = PersonPage.objects.get(title='Daniel Ricciardo')
        self.assertIn(kimi_raikkonen, staff_pages)
        self.assertIn(daniel_ricciardo, staff_pages)
        self.assertLess(
            staff_pages.index(kimi_raikkonen),
            staff_pages.index(daniel_ricciardo),
        )

    def test_leadership_page_board_members(self):
        response = self.client.get('/leadership/')
        board_member_live = PersonPage.objects.get(title='Board Member Live')
        self.assertEqual(list(response.context['people']), [board_member_live])

    def test_leadership_page_senior_management(self):
        response = self.client.get('/leadership/?show=senior-management')
        management_team_live = PersonPage.objects.get(title='Management Team Live')
        self.assertEqual(list(response.context['people']), [management_team_live])


class StaffPageRequestTests(WagtailPageTests):
    fixtures = ['staff.json']

    def setUp(self):
        home_page = HomePage.objects.get()
        home_page.numchild = 4
        home_page.save()

    def test_no_filter(self):
        response = self.client.get('/staff/')

        staff_names = [
            'Bianca Ayers',
            'Arham Buckner',
            'Angelina Clark',
            'Indi Dunn',
            'Teresa Ewing',
            'Chace Franco',
            'Maheen Gregory',
            'Julia Hogg',
            'Georgie Irwin',
            'Angela Jacobson',
            'Molly Keenan',
            'Roland Lovell',
            'Zainab Mckay',
            'Mahamed Neal',
            'Zayn Oconnor',
            'Eddie Parks',
            'Pamela Quinn',
            'Graham Rose',
            'Katlyn Stanton',
            'Beverly Travis',
            'Bryan Umbridge',
            'Deborah Villanueva',
            'Jamie Wilkins',
            'Frederick Xavier',
            'Jessie Yang',
            'Katharine Zhou',
        ]

        for name in staff_names:
            person_page = PersonPage.objects.get(title=name)
            self.assertIn(person_page, response.context['people'])

        self.assertEquals(len(response.context['people']), 26)

    def test_filter_a(self):
        response = self.client.get('/staff/?letter=a')
        bianca_ayers = PersonPage.objects.get(title='Bianca Ayers')
        self.assertIn(bianca_ayers, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_b(self):
        response = self.client.get('/staff/?letter=b')
        arham_buckner = PersonPage.objects.get(title='Arham Buckner')
        self.assertIn(arham_buckner, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_c(self):
        response = self.client.get('/staff/?letter=c')
        angelina_clark = PersonPage.objects.get(title='Angelina Clark')
        self.assertIn(angelina_clark, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_d(self):
        response = self.client.get('/staff/?letter=d')
        indi_dunn = PersonPage.objects.get(title='Indi Dunn')
        self.assertIn(indi_dunn, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_e(self):
        response = self.client.get('/staff/?letter=e')
        teresa_ewing = PersonPage.objects.get(title='Teresa Ewing')
        self.assertIn(teresa_ewing, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_f(self):
        response = self.client.get('/staff/?letter=f')
        chace_franco = PersonPage.objects.get(title='Chace Franco')
        self.assertIn(chace_franco, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_g(self):
        response = self.client.get('/staff/?letter=g')
        maheen_gregory = PersonPage.objects.get(title='Maheen Gregory')
        self.assertIn(maheen_gregory, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_h(self):
        response = self.client.get('/staff/?letter=h')
        julia_hogg = PersonPage.objects.get(title='Julia Hogg')
        self.assertIn(julia_hogg, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_i(self):
        response = self.client.get('/staff/?letter=i')
        georgie_irwin = PersonPage.objects.get(title='Georgie Irwin')
        self.assertIn(georgie_irwin, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_j(self):
        response = self.client.get('/staff/?letter=j')
        angela_jacobson = PersonPage.objects.get(title='Angela Jacobson')
        self.assertIn(angela_jacobson, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_k(self):
        response = self.client.get('/staff/?letter=k')
        molly_keenan = PersonPage.objects.get(title='Molly Keenan')
        self.assertIn(molly_keenan, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_l(self):
        response = self.client.get('/staff/?letter=l')
        roland_lovell = PersonPage.objects.get(title='Roland Lovell')
        self.assertIn(roland_lovell, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_m(self):
        response = self.client.get('/staff/?letter=m')
        zainab_mckay = PersonPage.objects.get(title='Zainab Mckay')
        self.assertIn(zainab_mckay, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_n(self):
        response = self.client.get('/staff/?letter=n')
        mahamed_neal = PersonPage.objects.get(title='Mahamed Neal')
        self.assertIn(mahamed_neal, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_o(self):
        response = self.client.get('/staff/?letter=o')
        zayn_oconnor = PersonPage.objects.get(title='Zayn Oconnor')
        self.assertIn(zayn_oconnor, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_p(self):
        response = self.client.get('/staff/?letter=p')
        eddie_parks = PersonPage.objects.get(title='Eddie Parks')
        self.assertIn(eddie_parks, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_q(self):
        response = self.client.get('/staff/?letter=q')
        pamela_quinn = PersonPage.objects.get(title='Pamela Quinn')
        self.assertIn(pamela_quinn, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_r(self):
        response = self.client.get('/staff/?letter=r')
        graham_rose = PersonPage.objects.get(title='Graham Rose')
        self.assertIn(graham_rose, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_s(self):
        response = self.client.get('/staff/?letter=s')
        katlyn_stanton = PersonPage.objects.get(title='Katlyn Stanton')
        self.assertIn(katlyn_stanton, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_t(self):
        response = self.client.get('/staff/?letter=t')
        beverly_travis = PersonPage.objects.get(title='Beverly Travis')
        self.assertIn(beverly_travis, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_u(self):
        response = self.client.get('/staff/?letter=u')
        bryan_umbridge = PersonPage.objects.get(title='Bryan Umbridge')
        self.assertIn(bryan_umbridge, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_v(self):
        response = self.client.get('/staff/?letter=v')
        deborah_villanueva = PersonPage.objects.get(title='Deborah Villanueva')
        self.assertIn(deborah_villanueva, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_w(self):
        response = self.client.get('/staff/?letter=w')
        jamie_wilkins = PersonPage.objects.get(title='Jamie Wilkins')
        self.assertIn(jamie_wilkins, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_x(self):
        response = self.client.get('/staff/?letter=x')
        frederick_xavier = PersonPage.objects.get(title='Frederick Xavier')
        self.assertIn(frederick_xavier, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_y(self):
        response = self.client.get('/staff/?letter=y')
        jessie_yang = PersonPage.objects.get(title='Jessie Yang')
        self.assertIn(jessie_yang, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_filter_z(self):
        response = self.client.get('/staff/?letter=z')
        katharine_zhou = PersonPage.objects.get(title='Katharine Zhou')
        self.assertIn(katharine_zhou, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_should_filter_first_character(self):
        response = self.client.get('/staff/?letter=ch')
        angelina_clark = PersonPage.objects.get(title='Angelina Clark')
        self.assertIn(angelina_clark, response.context['people'])
        self.assertEqual(len(response.context['people']), 1)

    def test_should_return_empty_list_with_number(self):
        response = self.client.get('/staff/?letter=12')
        self.assertEqual(len(response.context['people']), 0)


class PersonPageTests(WagtailPageTests):
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
