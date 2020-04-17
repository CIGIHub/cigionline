from core.models import BasicPage, HomePage
from wagtail.tests.utils import WagtailPageTests

from .models import PersonListPage, PersonPage


class PersonListPageTests(WagtailPageTests):
    fixtures = ["people.json"]

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
