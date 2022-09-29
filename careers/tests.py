from core.models import BasicPage
from home.models import HomePage
from wagtail.test.utils import WagtailPageTests

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
            {BasicPage, JobPostingPage},
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
