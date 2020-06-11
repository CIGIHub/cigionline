from core.models import HomePage
from wagtail.tests.utils import WagtailPageTests

from .models import JobPostingListPage, JobPostingPage


class JobPostingListPageTests(WagtailPageTests):
    def test_jobpostinglistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            JobPostingListPage,
            {HomePage},
        )

    def test_jobpostinglistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            JobPostingListPage,
            {JobPostingPage},
        )


class JobPostingPageTests(WagtailPageTests):
    def test_jobpostingpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            JobPostingPage,
            {JobPostingListPage},
        )

    def test_jobpostingpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            JobPostingPage,
            {},
        )
