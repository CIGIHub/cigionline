from core.models import BasicPage, HomePage
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import nested_form_data, rich_text

from .models import PeoplePage, PersonListPage, PersonPage
from .templatetags.people_tags import clean_phone_number


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
            if str(ae) == 'Creating a people.peoplepage returned a 403':
                pass
            else:
                raise ae


class PersonListPageTests(WagtailPageTests):
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
            if str(ae) == 'Creating a people.personlistpage returned a 403':
                pass
            else:
                raise ae

    def test_experts_page_should_not_show_live_board_member(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        board_member_live = PersonPage.objects.get(title='Board Member Live')
        self.assertNotIn(board_member_live, experts_page.person_pages)

    def test_experts_page_should_not_show_archived_board_member(self):

        experts_page = PersonListPage.objects.get(title='Experts')
        board_member_archived = PersonPage.objects.get(title='Board Member Archived')
        self.assertNotIn(board_member_archived, experts_page.person_pages)

    def test_experts_page_should_not_show_draft_board_member(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        board_member_draft = PersonPage.objects.get(title='Board Member Draft')
        self.assertNotIn(board_member_draft, experts_page.person_pages)

    def test_experts_page_should_show_live_cigi_chair(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        cigi_chair_live = PersonPage.objects.get(title='CIGI Chair Live')
        self.assertIn(cigi_chair_live, experts_page.person_pages)

    def test_experts_page_should_not_show_archived_cigi_chair(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        cigi_chair_archived = PersonPage.objects.get(title='CIGI Chair Archived')
        self.assertNotIn(cigi_chair_archived, experts_page.person_pages)

    def test_experts_page_should_not_show_draft_cigi_chair(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        cigi_chair_draft = PersonPage.objects.get(title='CIGI Chair Draft')
        self.assertNotIn(cigi_chair_draft, experts_page.person_pages)

    def test_experts_page_should_not_should_live_commission(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        commission_live = PersonPage.objects.get(title='Commission Live')
        self.assertNotIn(commission_live, experts_page.person_pages)

    def test_experts_page_should_not_should_archived_commission(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        commission_archived = PersonPage.objects.get(title='Commission Archived')
        self.assertNotIn(commission_archived, experts_page.person_pages)

    def test_experts_page_should_not_should_draft_commission(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        commission_draft = PersonPage.objects.get(title='Commission Draft')
        self.assertNotIn(commission_draft, experts_page.person_pages)

    def test_experts_page_should_show_live_expert(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        expert_live = PersonPage.objects.get(title='Expert Live')
        self.assertIn(expert_live, experts_page.person_pages)

    def test_experts_page_should_not_show_archived_expert(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        expert_archived = PersonPage.objects.get(title='Expert Archived')
        self.assertNotIn(expert_archived, experts_page.person_pages)

    def test_experts_page_should_not_show_draft_expert(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        expert_draft = PersonPage.objects.get(title='Expert Draft')
        self.assertNotIn(expert_draft, experts_page.person_pages)

    def test_experts_page_should_not_show_live_external_profile(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        external_profile_live = PersonPage.objects.get(title='External profile Live')
        self.assertNotIn(external_profile_live, experts_page.person_pages)

    def test_experts_page_should_not_show_archived_external_profile(self):

        experts_page = PersonListPage.objects.get(title='Experts')
        external_profile_archived = PersonPage.objects.get(title='External profile Archived')
        self.assertNotIn(external_profile_archived, experts_page.person_pages)

    def test_experts_page_should_not_show_draft_external_profile(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        external_profile_draft = PersonPage.objects.get(title='External profile Draft')
        self.assertNotIn(external_profile_draft, experts_page.person_pages)

    def test_experts_page_should_not_show_live_g20_expert(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        g20_expert_live = PersonPage.objects.get(title='G20 Expert Live')
        self.assertNotIn(g20_expert_live, experts_page.person_pages)

    def test_experts_page_should_not_show_archived_g20_expert(self):

        experts_page = PersonListPage.objects.get(title='Experts')
        g20_expert_archived = PersonPage.objects.get(title='G20 Expert Archived')
        self.assertNotIn(g20_expert_archived, experts_page.person_pages)

    def test_experts_page_should_not_show_draft_g20_expert(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        g20_expert_draft = PersonPage.objects.get(title='G20 Expert Draft')
        self.assertNotIn(g20_expert_draft, experts_page.person_pages)

    def test_experts_page_should_not_show_live_management_team(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        management_team_live = PersonPage.objects.get(title='Management Team Live')
        self.assertNotIn(management_team_live, experts_page.person_pages)

    def test_experts_page_should_not_show_archived_management_team(self):

        experts_page = PersonListPage.objects.get(title='Experts')
        management_team_archived = PersonPage.objects.get(title='Management Team Archived')
        self.assertNotIn(management_team_archived, experts_page.person_pages)

    def test_experts_page_should_not_show_draft_management_team(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        management_team_draft = PersonPage.objects.get(title='Management Team Draft')
        self.assertNotIn(management_team_draft, experts_page.person_pages)

    def test_experts_page_should_not_show_live_media_contact(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        media_contact_live = PersonPage.objects.get(title='Media Contact Live')
        self.assertNotIn(media_contact_live, experts_page.person_pages)

    def test_experts_page_should_not_show_archived_media_contact(self):

        experts_page = PersonListPage.objects.get(title='Experts')
        media_contact_archived = PersonPage.objects.get(title='Media Contact Archived')
        self.assertNotIn(media_contact_archived, experts_page.person_pages)

    def test_experts_page_should_not_show_draft_media_contact(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        media_contact_draft = PersonPage.objects.get(title='Media Contact Draft')
        self.assertNotIn(media_contact_draft, experts_page.person_pages)

    def test_experts_page_should_not_show_live_person(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        person_live = PersonPage.objects.get(title='Person Live')
        self.assertNotIn(person_live, experts_page.person_pages)

    def test_experts_page_should_not_show_archived_person(self):

        experts_page = PersonListPage.objects.get(title='Experts')
        person_archived = PersonPage.objects.get(title='Person Archived')
        self.assertNotIn(person_archived, experts_page.person_pages)

    def test_experts_page_should_not_show_draft_person(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        person_draft = PersonPage.objects.get(title='Person Draft')
        self.assertNotIn(person_draft, experts_page.person_pages)

    def test_experts_page_should_not_show_live_program_director(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        program_director_live = PersonPage.objects.get(title='Program Director Live')
        self.assertNotIn(program_director_live, experts_page.person_pages)

    def test_experts_page_should_not_show_archived_program_director(self):

        experts_page = PersonListPage.objects.get(title='Experts')
        program_director_archived = PersonPage.objects.get(title='Program Director Archived')
        self.assertNotIn(program_director_archived, experts_page.person_pages)

    def test_experts_page_should_not_show_draft_program_director(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        program_director_draft = PersonPage.objects.get(title='Program Director Draft')
        self.assertNotIn(program_director_draft, experts_page.person_pages)

    def test_experts_page_should_not_show_live_program_manager(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        program_manager_live = PersonPage.objects.get(title='Program Manager Live')
        self.assertNotIn(program_manager_live, experts_page.person_pages)

    def test_experts_page_should_not_show_archived_program_manager(self):

        experts_page = PersonListPage.objects.get(title='Experts')
        program_manager_archived = PersonPage.objects.get(title='Program Manager Archived')
        self.assertNotIn(program_manager_archived, experts_page.person_pages)

    def test_experts_page_should_not_show_draft_program_manager(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        program_manager_draft = PersonPage.objects.get(title='Program Manager Draft')
        self.assertNotIn(program_manager_draft, experts_page.person_pages)

    def test_experts_page_should_not_show_live_research_advisor(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        research_advisor_live = PersonPage.objects.get(title='Research Advisor Live')
        self.assertNotIn(research_advisor_live, experts_page.person_pages)

    def test_experts_page_should_not_show_archived_research_advisor(self):

        experts_page = PersonListPage.objects.get(title='Experts')
        research_advisor_archived = PersonPage.objects.get(title='Research Advisor Archived')
        self.assertNotIn(research_advisor_archived, experts_page.person_pages)

    def test_experts_page_should_not_show_draft_research_advisor(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        research_advisor_draft = PersonPage.objects.get(title='Research Advisor Draft')
        self.assertNotIn(research_advisor_draft, experts_page.person_pages)

    def test_experts_page_should_not_show_live_research_associate(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        research_associate_live = PersonPage.objects.get(title='Research Associate Live')
        self.assertNotIn(research_associate_live, experts_page.person_pages)

    def test_experts_page_should_not_show_archived_research_associate(self):

        experts_page = PersonListPage.objects.get(title='Experts')
        research_associate_archived = PersonPage.objects.get(title='Research Associate Archived')
        self.assertNotIn(research_associate_archived, experts_page.person_pages)

    def test_experts_page_should_not_show_draft_research_associate(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        research_associate_draft = PersonPage.objects.get(title='Research Associate Draft')
        self.assertNotIn(research_associate_draft, experts_page.person_pages)

    def test_experts_page_should_not_show_live_research_fellow(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        research_fellow_live = PersonPage.objects.get(title='Research Fellow Live')
        self.assertNotIn(research_fellow_live, experts_page.person_pages)

    def test_experts_page_should_not_show_archived_research_fellow(self):

        experts_page = PersonListPage.objects.get(title='Experts')
        research_fellow_archived = PersonPage.objects.get(title='Research Fellow Archived')
        self.assertNotIn(research_fellow_archived, experts_page.person_pages)

    def test_experts_page_should_not_show_draft_research_fellow(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        research_fellow_draft = PersonPage.objects.get(title='Research Fellow Draft')
        self.assertNotIn(research_fellow_draft, experts_page.person_pages)

    def test_experts_page_should_not_show_live_speaker(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        speaker_live = PersonPage.objects.get(title='Speaker Live')
        self.assertNotIn(speaker_live, experts_page.person_pages)

    def test_experts_page_should_not_show_archived_speaker(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        speaker_archived = PersonPage.objects.get(title='Speaker Archived')
        self.assertNotIn(speaker_archived, experts_page.person_pages)

    def test_experts_page_should_not_show_draft_speaker(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        speaker_draft = PersonPage.objects.get(title='Speaker Draft')
        self.assertNotIn(speaker_draft, experts_page.person_pages)

    def test_experts_page_should_not_show_live_staff(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        staff_live = PersonPage.objects.get(title='Staff Live')
        self.assertNotIn(staff_live, experts_page.person_pages)

    def test_experts_page_should_not_show_archived_staff(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        staff_archived = PersonPage.objects.get(title='Staff Archived')
        self.assertNotIn(staff_archived, experts_page.person_pages)

    def test_experts_page_should_not_show_draft_staff(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        staff_draft = PersonPage.objects.get(title='Staff Draft')
        self.assertNotIn(staff_draft, experts_page.person_pages)

    def test_experts_page_order_accent_insensitive(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        expert_pages = list(experts_page.person_pages)
        kimi_raikkonen = PersonPage.objects.get(title='Kimi Räikkönen')
        daniel_ricciardo = PersonPage.objects.get(title='Daniel Ricciardo')
        self.assertIn(kimi_raikkonen, expert_pages)
        self.assertIn(daniel_ricciardo, expert_pages)
        self.assertLess(
            expert_pages.index(kimi_raikkonen),
            expert_pages.index(daniel_ricciardo),
        )

    def test_experts_page_should_not_show_board_members(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        self.assertEqual(list(experts_page.board_members), [])

    def test_experts_page_should_not_show_senior_management(self):
        experts_page = PersonListPage.objects.get(title='Experts')
        self.assertEqual(list(experts_page.senior_management), [])

    def test_staff_directory_page_should_not_show_live_board_member(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        board_member_live = PersonPage.objects.get(title='Board Member Live')
        self.assertNotIn(board_member_live, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_archived_board_member(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        board_member_archived = PersonPage.objects.get(title='Board Member Archived')
        self.assertNotIn(board_member_archived, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_draft_board_member(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        board_member_draft = PersonPage.objects.get(title='Board Member Draft')
        self.assertNotIn(board_member_draft, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_live_cigi_chair(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        cigi_chair_live = PersonPage.objects.get(title='CIGI Chair Live')
        self.assertNotIn(cigi_chair_live, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_archived_cigi_chair(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        cigi_chair_archived = PersonPage.objects.get(title='CIGI Chair Archived')
        self.assertNotIn(cigi_chair_archived, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_draft_cigi_chair(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        cigi_chair_draft = PersonPage.objects.get(title='CIGI Chair Draft')
        self.assertNotIn(cigi_chair_draft, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_live_commission(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        commission_live = PersonPage.objects.get(title='Commission Live')
        self.assertNotIn(commission_live, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_archived_commission(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        commission_archived = PersonPage.objects.get(title='Commission Archived')
        self.assertNotIn(commission_archived, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_draft_commission(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        commission_draft = PersonPage.objects.get(title='Commission Draft')
        self.assertNotIn(commission_draft, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_live_expert(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        expert_live = PersonPage.objects.get(title='Expert Live')
        self.assertNotIn(expert_live, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_archived_expert(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        expert_archived = PersonPage.objects.get(title='Expert Archived')
        self.assertNotIn(expert_archived, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_draft_expert(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        expert_draft = PersonPage.objects.get(title='Expert Draft')
        self.assertNotIn(expert_draft, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_live_external_profile(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        external_profile_live = PersonPage.objects.get(title='External profile Live')
        self.assertNotIn(external_profile_live, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_archived_external_profile(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        external_profile_archived = PersonPage.objects.get(title='External profile Archived')
        self.assertNotIn(external_profile_archived, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_draft_external_profile(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        external_profile_draft = PersonPage.objects.get(title='External profile Draft')
        self.assertNotIn(external_profile_draft, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_live_g20_expert(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        g20_expert_live = PersonPage.objects.get(title='G20 Expert Live')
        self.assertNotIn(g20_expert_live, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_archived_g20_expert(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        g20_expert_archived = PersonPage.objects.get(title='G20 Expert Archived')
        self.assertNotIn(g20_expert_archived, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_draft_g20_expert(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        g20_expert_draft = PersonPage.objects.get(title='G20 Expert Draft')
        self.assertNotIn(g20_expert_draft, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_live_management_team(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        management_team_live = PersonPage.objects.get(title='Management Team Live')
        self.assertNotIn(management_team_live, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_archived_management_team(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        management_team_archived = PersonPage.objects.get(title='Management Team Archived')
        self.assertNotIn(management_team_archived, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_draft_management_team(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        management_team_draft = PersonPage.objects.get(title='Management Team Draft')
        self.assertNotIn(management_team_draft, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_live_media_contact(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        media_contact_live = PersonPage.objects.get(title='Media Contact Live')
        self.assertNotIn(media_contact_live, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_archived_media_contact(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        media_contact_archived = PersonPage.objects.get(title='Media Contact Archived')
        self.assertNotIn(media_contact_archived, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_draft_media_contact(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        media_contact_draft = PersonPage.objects.get(title='Media Contact Draft')
        self.assertNotIn(media_contact_draft, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_live_person(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        person_live = PersonPage.objects.get(title='Person Live')
        self.assertNotIn(person_live, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_archived_person(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        person_archived = PersonPage.objects.get(title='Person Archived')
        self.assertNotIn(person_archived, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_draft_person(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        person_draft = PersonPage.objects.get(title='Person Draft')
        self.assertNotIn(person_draft, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_live_program_director(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        program_director_live = PersonPage.objects.get(title='Program Director Live')
        self.assertNotIn(program_director_live, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_archived_program_director(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        program_director_archived = PersonPage.objects.get(title='Program Director Archived')
        self.assertNotIn(program_director_archived, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_draft_program_director(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        program_director_draft = PersonPage.objects.get(title='Program Director Draft')
        self.assertNotIn(program_director_draft, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_live_program_manager(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        program_manager_live = PersonPage.objects.get(title='Program Manager Live')
        self.assertNotIn(program_manager_live, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_archived_program_manager(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        program_manager_archived = PersonPage.objects.get(title='Program Manager Archived')
        self.assertNotIn(program_manager_archived, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_draft_program_manager(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        program_manager_draft = PersonPage.objects.get(title='Program Manager Draft')
        self.assertNotIn(program_manager_draft, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_live_research_advisor(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        research_advisor_live = PersonPage.objects.get(title='Research Advisor Live')
        self.assertNotIn(research_advisor_live, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_archived_research_advisor(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        research_advisor_archived = PersonPage.objects.get(title='Research Advisor Archived')
        self.assertNotIn(research_advisor_archived, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_draft_research_advisor(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        research_advisor_draft = PersonPage.objects.get(title='Research Advisor Draft')
        self.assertNotIn(research_advisor_draft, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_live_research_associate(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        research_associate_live = PersonPage.objects.get(title='Research Associate Live')
        self.assertNotIn(research_associate_live, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_archived_research_associate(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        research_associate_archived = PersonPage.objects.get(title='Research Associate Archived')
        self.assertNotIn(research_associate_archived, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_draft_research_associate(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        research_associate_draft = PersonPage.objects.get(title='Research Associate Draft')
        self.assertNotIn(research_associate_draft, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_live_research_fellow(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        research_fellow_live = PersonPage.objects.get(title='Research Fellow Live')
        self.assertNotIn(research_fellow_live, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_archived_research_fellow(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        research_fellow_archived = PersonPage.objects.get(title='Research Fellow Archived')
        self.assertNotIn(research_fellow_archived, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_draft_research_fellow(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        research_fellow_draft = PersonPage.objects.get(title='Research Fellow Draft')
        self.assertNotIn(research_fellow_draft, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_live_speaker(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        speaker_live = PersonPage.objects.get(title='Speaker Live')
        self.assertNotIn(speaker_live, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_archived_speaker(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        speaker_archived = PersonPage.objects.get(title='Speaker Archived')
        self.assertNotIn(speaker_archived, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_draft_speaker(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        speaker_draft = PersonPage.objects.get(title='Speaker Draft')
        self.assertNotIn(speaker_draft, staff_directory_page.person_pages)

    def test_staff_directory_page_should_show_live_staff(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        staff_live = PersonPage.objects.get(title='Staff Live')
        self.assertIn(staff_live, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_archived_staff(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        staff_archived = PersonPage.objects.get(title='Staff Archived')
        self.assertNotIn(staff_archived, staff_directory_page.person_pages)

    def test_staff_directory_page_should_not_show_draft_staff(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        staff_draft = PersonPage.objects.get(title='Staff Draft')
        self.assertNotIn(staff_draft, staff_directory_page.person_pages)

    def test_staff_directory_page_order_accent_insensitive(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        staff_pages = list(staff_directory_page.person_pages)
        kimi_raikkonen = PersonPage.objects.get(title='Kimi Räikkönen')
        daniel_ricciardo = PersonPage.objects.get(title='Daniel Ricciardo')
        self.assertIn(kimi_raikkonen, staff_pages)
        self.assertIn(daniel_ricciardo, staff_pages)
        self.assertLess(
            staff_pages.index(kimi_raikkonen),
            staff_pages.index(daniel_ricciardo),
        )

    def test_staff_directory_page_should_not_show_board_members(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        self.assertEqual(list(staff_directory_page.board_members), [])

    def test_staff_directory_page_should_not_show_senior_management(self):
        staff_directory_page = PersonListPage.objects.get(title='Staff Directory')
        self.assertEqual(list(staff_directory_page.senior_management), [])

    def test_leadership_page_board_members(self):
        leadership_page = PersonListPage.objects.get(title='Leadership')
        board_member_live = PersonPage.objects.get(title='Board Member Live')
        self.assertEqual(list(leadership_page.board_members), [board_member_live])

    def test_leadership_page_senior_management(self):
        leadership_page = PersonListPage.objects.get(title='Leadership')
        management_team_live = PersonPage.objects.get(title='Management Team Live')
        self.assertEqual(list(leadership_page.senior_management), [management_team_live])


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

class PeopleTagsTests(WagtailPageTests):
    def test_clean_phone_filter_blank_string(self):
        self.assertEqual('', clean_phone_number(''))

    def test_clean_phone_filter_number_with_dots(self):
        self.assertEqual('1 2 3 4 5', clean_phone_number('1.2.3.4.5'))
    
    def test_clean_phone_filter_number_with_capital_text(self):
        self.assertEqual('1 2 3 4 5 ext 6789', clean_phone_number('1.2.3.4.5 EXT 6789'))
