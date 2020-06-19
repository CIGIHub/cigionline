from core.models import HomePage
from wagtail.tests.utils import WagtailPageTests

from .models import EventListPage, EventPage


class EventListPageTests(WagtailPageTests):
    def test_eventlistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            EventListPage,
            {HomePage},
        )

    def test_eventlistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            EventListPage,
            {EventPage},
        )


class EventPageTests(WagtailPageTests):
    def test_eventpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            EventPage,
            {EventListPage},
        )

    def test_eventpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            EventPage,
            {},
        )
