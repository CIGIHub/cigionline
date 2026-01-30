from datetime import datetime
from home.models import HomePage, Think7HomePage
from wagtail.test.utils import WagtailPageTestCase
from django.test import TestCase

from .models import EventListPage, EventPage
from .email_rendering import render_streamfield_email_html

from unittest.mock import patch


class DuplicateRegistrationTests(TestCase):
    """Duplicate email registrations should not create multiple active rows."""

    @patch("events.models.send_confirmation_email")
    def test_duplicate_registration_does_not_create_second_registrant(self, send_mock):
        from events.models import EventPage, RegistrationType, Registrant
        from wagtail.models import Site

        # Minimal Site/Page setup so the EventPage route can resolve.
        root = Site.objects.get(is_default_site=True).root_page
        event = EventPage(title="Dup Test Event")
        root.add_child(instance=event)
        event.save_revision().publish()

        reg_type = RegistrationType(event=event, name="General", slug="general", sort_order=0, is_public=True)
        reg_type.save()

        # Pre-existing (active) registrant
        Registrant.objects.create(
            event=event,
            registration_type=reg_type,
            email="test@example.com",
            first_name="A",
            last_name="B",
            status=Registrant.Status.CONFIRMED,
        )

        before = Registrant.objects.filter(event=event, email__iexact="test@example.com").count()

        # Post again with same email
        resp = self.client.post(
            f"{event.url}register/type/{reg_type.slug}/",
            data={
                "first_name": "New",
                "last_name": "User",
                "email": "test@example.com",
                "website": "",
            },
        )

        self.assertEqual(resp.status_code, 302)
        after = Registrant.objects.filter(event=event, email__iexact="test@example.com").count()
        self.assertEqual(before, after)
        self.assertTrue(send_mock.called)

    @patch("events.models.send_confirmation_email")
    def test_duplicate_registration_allows_if_cancelled(self, send_mock):
        from events.models import EventPage, RegistrationType, Registrant
        from wagtail.models import Site

        root = Site.objects.get(is_default_site=True).root_page
        event = EventPage(title="Dup Cancelled Event")
        root.add_child(instance=event)
        event.save_revision().publish()

        reg_type = RegistrationType(event=event, name="General", slug="general", sort_order=0, is_public=True)
        reg_type.save()

        Registrant.objects.create(
            event=event,
            registration_type=reg_type,
            email="test@example.com",
            status=Registrant.Status.CANCELLED,
        )

        before = Registrant.objects.filter(event=event, email__iexact="test@example.com").count()

        resp = self.client.post(
            f"{event.url}register/type/{reg_type.slug}/",
            data={
                "first_name": "New",
                "last_name": "User",
                "email": "test@example.com",
                "website": "",
            },
        )
        self.assertEqual(resp.status_code, 302)
        after = Registrant.objects.filter(event=event, email__iexact="test@example.com").count()
        self.assertEqual(after, before + 1)


class EventListPageTests(WagtailPageTestCase):
    def test_eventlistpage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            EventListPage,
            {HomePage, Think7HomePage},
        )

    def test_eventlistpage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            EventListPage,
            {EventPage},
        )


class EventPageTests(WagtailPageTestCase):
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


class EventsAPITests(WagtailPageTestCase):
    fixtures = ['events_search_table.json']

    @patch('events.views.timezone.now', return_value=datetime(2020, 1, 1))
    def test_events_api(self, _):
        response = self.client.get('/api/events/')
        self.assertEqual(response.status_code, 200)
        actual_response = response.json()
        expected_response = {
            "meta": {"total_count": 3},
            "items": [
                {
                    "title": "Test Event 1",
                    "url": "/events/event-1/",
                    "publishing_date": "2020-01-02T13:00:00+00:00"
                },
                {
                    "title": "Test Event 2",
                    "url": "/events/event-2/",
                    "publishing_date": "2020-01-15T13:00:00+00:00",
                },
                {
                    "title": "Test Event 3 - Big Tech",
                    "url": "/events/event-3/",
                    "publishing_date": "2020-01-30T13:00:00+00:00"
                },
            ]
        }
        self.assertEqual(actual_response, expected_response)

    def get_api_response(self, month, year):
        response = self.client.get(f'/api/events/?month={month}&year={year}')
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_events_api_by_month(self):
        response_1 = self.get_api_response(1, 2020)
        self.assertEqual(response_1['meta']['total_count'], 3)
        self.assertEqual(len(response_1['items']), 3)

        response_2 = self.get_api_response(2, 2020)
        self.assertEqual(response_2['meta']['total_count'], 4)
        self.assertEqual(len(response_2['items']), 4)


class EmailTemplateRenderingTests(WagtailPageTestCase):
    def test_streamfield_email_rendering_outputs_email_safe_wrapper(self):
        class DummyTemplate:
            def __init__(self, body):
                self.body = body

        # Using StreamValue-like data: Wagtail StreamField will accept a list of dicts
        # when assigning to the field on a real model. For this renderer, we just need
        # something iterable with block_type/value attributes. We'll use the StreamField
        # itself from the EmailTemplate model indirectly by building minimal objects.
        class B:
            def __init__(self, block_type, value):
                self.block_type = block_type
                self.value = value

        dummy = DummyTemplate(
            body=[
                B("heading", {"text": "Hello", "level": "h2"}),
                B("paragraph", "<p>Thanks for registering.</p>"),
                B("button", {"text": "View details", "url": "https://example.com"}),
                B("image", {"image": None, "image_url": "https://example.com/logo.png", "alt": "Logo", "alignment": "center", "max_width": 200, "link": ""}),
                B("divider", None),
            ]
        )

        html, text = render_streamfield_email_html(
            template_obj=dummy,
            ctx={
                "event": type("E", (), {"title": "Test Event", "get_site": type("S", (), {"root_url": "https://example.com"})()})(),
                "registrant": type("R", (), {"first_name": "Jane", "email": "jane@example.com"})(),
                "registration_type": type("T", (), {"name": "General"})(),
                "confirmed": True,
            },
        )

        self.assertIn("<table", html)
        self.assertIn("View details", html)
        self.assertIn("https://example.com/logo.png", html)
        self.assertIn("Test Event", html)
        self.assertTrue(len(text) > 0)

        response_3 = self.get_api_response(12, 2010)
        self.assertEqual(response_3['meta']['total_count'], 0)
        self.assertEqual(len(response_3['items']), 0)

# class EventPageViewSetTests(WagtailPageTestCase):
#     fixtures = ['events_search_table.json']
#     limit = 24
#
#     def get_api_url(self, page):
#         offset = (page - 1) * self.limit
#         return f'/api/events/?limit={self.limit}&offset={offset}&fields=publishing_date,title,topics(title,url),url'
#
#     def verify_res_items(self, responseItems, expectedItems):
#         for i in range(len(expectedItems)):
#             self.assertEqual(responseItems[i]['title'], expectedItems[i]['title'])
#             self.assertEqual(responseItems[i]['url'], expectedItems[i]['url'])
#             self.assertEqual(responseItems[i]['publishing_date'], expectedItems[i]['publishing_date'])
#
#             self.assertEqual(len(responseItems[i]['topics']), len(expectedItems[i]['topics']), f'Length of topics: {expectedItems[i]["title"]}')
#             # Verify that the expected topic titles were returned in the response
#             for topicTitle in expectedItems[i]['topics']:
#                 self.assertTrue(any(topic['title'] == topicTitle for topic in responseItems[i]['topics']), f'Could not find topic:{topicTitle} for publication:{expectedItems[i]["title"]}')
#
#     def test_page_1_query_returns_200(self):
#         res = self.client.get(self.get_api_url(1))
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 30)
#         self.assertEqual(len(resJson['items']), 24)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-12-31T08:00:00-05:00',
#             'title': 'Test Event 30',
#             'topics': ['Test Topic 3'],
#             'url': '/events/event-30/',
#         }, {
#             'publishing_date': '2020-12-30T08:00:00-05:00',
#             'title': 'Test Event 29',
#             'topics': ['Test Topic 2'],
#             'url': '/events/event-29/',
#         }, {
#             'publishing_date': '2020-12-25T08:00:00-05:00',
#             'title': 'Test Event 28',
#             'topics': ['Test Topic 1', 'Test Topic 2'],
#             'url': '/events/event-28/',
#         }, {
#             'publishing_date': '2020-12-15T08:00:00-05:00',
#             'title': 'Test Event 27',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-27/',
#         }, {
#             'publishing_date': '2020-12-04T08:00:00-05:00',
#             'title': 'Test Event 26',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-26/',
#         }, {
#             'publishing_date': '2020-11-17T08:00:00-05:00',
#             'title': 'Test Event 25',
#             'topics': ['Test Topic 3'],
#             'url': '/events/event-25/',
#         }, {
#             'publishing_date': '2020-10-30T08:00:00-04:00',
#             'title': 'Test Event 24',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-24/',
#         }, {
#             'publishing_date': '2020-10-27T08:00:00-04:00',
#             'title': 'Test Event 23',
#             'topics': ['Test Topic 3'],
#             'url': '/events/event-23/',
#         }, {
#             'publishing_date': '2020-09-24T08:00:00-04:00',
#             'title': 'Test Event 22 - Big Tech',
#             'topics': ['Test Topic 3'],
#             'url': '/events/event-22/',
#         }, {
#             'publishing_date': '2020-09-18T08:00:00-04:00',
#             'title': 'Test Event 21',
#             'topics': ['Test Topic 2'],
#             'url': '/events/event-21/',
#         }, {
#             'publishing_date': '2020-09-16T08:00:00-04:00',
#             'title': 'Test Event 20',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-20/',
#         }, {
#             'publishing_date': '2020-09-08T08:00:00-04:00',
#             'title': 'Test Event 19',
#             'topics': ['Test Topic 2', 'Test Topic 3'],
#             'url': '/events/event-19/',
#         }, {
#             'publishing_date': '2020-09-01T08:00:00-04:00',
#             'title': 'Test Event 18',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-18/',
#         }, {
#             'publishing_date': '2020-08-04T08:00:00-04:00',
#             'title': 'Test Event 17',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-17/',
#         }, {
#             'publishing_date': '2020-07-09T08:00:00-04:00',
#             'title': 'Test Event 16',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-16/',
#         }, {
#             'publishing_date': '2020-06-26T08:00:00-04:00',
#             'title': 'Test Event 15',
#             'topics': ['Test Topic 2'],
#             'url': '/events/event-15/',
#         }, {
#             'publishing_date': '2020-06-15T08:00:00-04:00',
#             'title': 'Test Event 14',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-14/',
#         }, {
#             'publishing_date': '2020-05-25T08:00:00-04:00',
#             'title': 'Test Event 13',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-13/',
#         }, {
#             'publishing_date': '2020-05-21T08:00:00-04:00',
#             'title': 'Test Event 12',
#             'topics': ['Test Topic 3'],
#             'url': '/events/event-12/',
#         }, {
#             'publishing_date': '2020-04-23T08:00:00-04:00',
#             'title': 'Test Event 11',
#             'topics': ['Test Topic 3'],
#             'url': '/events/event-11/',
#         }, {
#             'publishing_date': '2020-04-13T08:00:00-04:00',
#             'title': 'Test Event 10',
#             'topics': ['Test Topic 3'],
#             'url': '/events/event-10/',
#         }, {
#             'publishing_date': '2020-03-18T08:00:00-04:00',
#             'title': 'Test Event 9',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-9/',
#         }, {
#             'publishing_date': '2020-03-12T08:00:00-04:00',
#             'title': 'Test Event 8',
#             'topics': ['Test Topic 2'],
#             'url': '/events/event-8/',
#         }, {
#             'publishing_date': '2020-02-21T08:00:00-05:00',
#             'title': 'Test Event 7',
#             'topics': ['Test Topic 2'],
#             'url': '/events/event-7/',
#         }])
#
#     def test_page_2_query_returns_200(self):
#         res = self.client.get(self.get_api_url(2))
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 30)
#         self.assertEqual(len(resJson['items']), 6)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-02-20T08:00:00-05:00',
#             'title': 'Test Event 6',
#             'topics': ['Test Topic 3'],
#             'url': '/events/event-6/',
#         }, {
#             'publishing_date': '2020-02-19T08:00:00-05:00',
#             'title': 'Test Event 5',
#             'topics': ['Test Topic 3'],
#             'url': '/events/event-5/',
#         }, {
#             'publishing_date': '2020-02-13T08:00:00-05:00',
#             'title': 'Test Event 4',
#             'topics': ['Test Topic 2'],
#             'url': '/events/event-4/',
#         }, {
#             'publishing_date': '2020-01-30T08:00:00-05:00',
#             'title': 'Test Event 3 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-3/',
#         }, {
#             'publishing_date': '2020-01-15T08:00:00-05:00',
#             'title': 'Test Event 2',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-2/',
#         }, {
#             'publishing_date': '2020-01-02T08:00:00-05:00',
#             'title': 'Test Event 1',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-1/',
#         }])
#
#     def test_page_3_returns_200(self):
#         res = self.client.get(self.get_api_url(3))
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 30)
#         self.assertEqual(len(resJson['items']), 0)
#
#     def test_search_query_returns_200(self):
#         res = self.client.get(f'{self.get_api_url(1)}&search=big+tech')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 3)
#         self.assertEqual(len(resJson['items']), 3)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-09-24T08:00:00-04:00',
#             'title': 'Test Event 22 - Big Tech',
#             'topics': ['Test Topic 3'],
#             'url': '/events/event-22/',
#         }, {
#             'publishing_date': '2020-01-30T08:00:00-05:00',
#             'title': 'Test Event 3 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-3/',
#         }, {
#             'publishing_date': '2020-06-15T08:00:00-04:00',
#             'title': 'Test Event 14',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-14/',
#         }])
#
#     def test_filter_topic_1_returns_200(self):
#         topic1 = TopicPage.objects.get(title='Test Topic 1')
#         res = self.client.get(f'{self.get_api_url(1)}&topics={topic1.id}')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 14)
#         self.assertEqual(len(resJson['items']), 14)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-12-25T08:00:00-05:00',
#             'title': 'Test Event 28',
#             'topics': ['Test Topic 1', 'Test Topic 2'],
#             'url': '/events/event-28/',
#         }, {
#             'publishing_date': '2020-12-15T08:00:00-05:00',
#             'title': 'Test Event 27',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-27/',
#         }, {
#             'publishing_date': '2020-12-04T08:00:00-05:00',
#             'title': 'Test Event 26',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-26/',
#         }, {
#             'publishing_date': '2020-10-30T08:00:00-04:00',
#             'title': 'Test Event 24',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-24/',
#         }, {
#             'publishing_date': '2020-09-16T08:00:00-04:00',
#             'title': 'Test Event 20',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-20/',
#         }, {
#             'publishing_date': '2020-09-01T08:00:00-04:00',
#             'title': 'Test Event 18',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-18/',
#         }, {
#             'publishing_date': '2020-08-04T08:00:00-04:00',
#             'title': 'Test Event 17',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-17/',
#         }, {
#             'publishing_date': '2020-07-09T08:00:00-04:00',
#             'title': 'Test Event 16',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-16/',
#         }, {
#             'publishing_date': '2020-06-15T08:00:00-04:00',
#             'title': 'Test Event 14',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-14/',
#         }, {
#             'publishing_date': '2020-05-25T08:00:00-04:00',
#             'title': 'Test Event 13',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-13/',
#         }, {
#             'publishing_date': '2020-03-18T08:00:00-04:00',
#             'title': 'Test Event 9',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-9/',
#         }, {
#             'publishing_date': '2020-01-30T08:00:00-05:00',
#             'title': 'Test Event 3 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-3/',
#         }, {
#             'publishing_date': '2020-01-15T08:00:00-05:00',
#             'title': 'Test Event 2',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-2/',
#         }, {
#             'publishing_date': '2020-01-02T08:00:00-05:00',
#             'title': 'Test Event 1',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-1/',
#         }])
#
#     def test_filter_topic_2_returns_200(self):
#         topic2 = TopicPage.objects.get(title='Test Topic 2')
#         res = self.client.get(f'{self.get_api_url(1)}&topics={topic2.id}')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 8)
#         self.assertEqual(len(resJson['items']), 8)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-12-30T08:00:00-05:00',
#             'title': 'Test Event 29',
#             'topics': ['Test Topic 2'],
#             'url': '/events/event-29/',
#         }, {
#             'publishing_date': '2020-12-25T08:00:00-05:00',
#             'title': 'Test Event 28',
#             'topics': ['Test Topic 1', 'Test Topic 2'],
#             'url': '/events/event-28/',
#         }, {
#             'publishing_date': '2020-09-18T08:00:00-04:00',
#             'title': 'Test Event 21',
#             'topics': ['Test Topic 2'],
#             'url': '/events/event-21/',
#         }, {
#             'publishing_date': '2020-09-08T08:00:00-04:00',
#             'title': 'Test Event 19',
#             'topics': ['Test Topic 2', 'Test Topic 3'],
#             'url': '/events/event-19/',
#         }, {
#             'publishing_date': '2020-06-26T08:00:00-04:00',
#             'title': 'Test Event 15',
#             'topics': ['Test Topic 2'],
#             'url': '/events/event-15/',
#         }, {
#             'publishing_date': '2020-03-12T08:00:00-04:00',
#             'title': 'Test Event 8',
#             'topics': ['Test Topic 2'],
#             'url': '/events/event-8/',
#         }, {
#             'publishing_date': '2020-02-21T08:00:00-05:00',
#             'title': 'Test Event 7',
#             'topics': ['Test Topic 2'],
#             'url': '/events/event-7/',
#         }, {
#             'publishing_date': '2020-02-13T08:00:00-05:00',
#             'title': 'Test Event 4',
#             'topics': ['Test Topic 2'],
#             'url': '/events/event-4/',
#         }])
#
#     def test_filter_topic_3_returns_200(self):
#         topic3 = TopicPage.objects.get(title='Test Topic 3')
#         res = self.client.get(f'{self.get_api_url(1)}&topics={topic3.id}')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 10)
#         self.assertTrue(len(resJson['items']), 10)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-12-31T08:00:00-05:00',
#             'title': 'Test Event 30',
#             'topics': ['Test Topic 3'],
#             'url': '/events/event-30/',
#         }, {
#             'publishing_date': '2020-11-17T08:00:00-05:00',
#             'title': 'Test Event 25',
#             'topics': ['Test Topic 3'],
#             'url': '/events/event-25/',
#         }, {
#             'publishing_date': '2020-10-27T08:00:00-04:00',
#             'title': 'Test Event 23',
#             'topics': ['Test Topic 3'],
#             'url': '/events/event-23/',
#         }, {
#             'publishing_date': '2020-09-24T08:00:00-04:00',
#             'title': 'Test Event 22 - Big Tech',
#             'topics': ['Test Topic 3'],
#             'url': '/events/event-22/',
#         }, {
#             'publishing_date': '2020-09-08T08:00:00-04:00',
#             'title': 'Test Event 19',
#             'topics': ['Test Topic 2', 'Test Topic 3'],
#             'url': '/events/event-19/',
#         }, {
#             'publishing_date': '2020-05-21T08:00:00-04:00',
#             'title': 'Test Event 12',
#             'topics': ['Test Topic 3'],
#             'url': '/events/event-12/',
#         }, {
#             'publishing_date': '2020-04-23T08:00:00-04:00',
#             'title': 'Test Event 11',
#             'topics': ['Test Topic 3'],
#             'url': '/events/event-11/',
#         }, {
#             'publishing_date': '2020-04-13T08:00:00-04:00',
#             'title': 'Test Event 10',
#             'topics': ['Test Topic 3'],
#             'url': '/events/event-10/',
#         }, {
#             'publishing_date': '2020-02-20T08:00:00-05:00',
#             'title': 'Test Event 6',
#             'topics': ['Test Topic 3'],
#             'url': '/events/event-6/',
#         }, {
#             'publishing_date': '2020-02-19T08:00:00-05:00',
#             'title': 'Test Event 5',
#             'topics': ['Test Topic 3'],
#             'url': '/events/event-5/',
#         }])
#
#     def test_search_and_filter_topics_returns_200(self):
#         topic1 = TopicPage.objects.get(title='Test Topic 1')
#         res = self.client.get(f'{self.get_api_url(1)}&search=big+tech&topics={topic1.id}')
#         self.assertEqual(res.status_code, 200)
#         resJson = res.json()
#         self.assertEqual(resJson['meta']['total_count'], 2)
#         self.assertEqual(len(resJson['items']), 2)
#
#         self.verify_res_items(resJson['items'], [{
#             'publishing_date': '2020-01-30T08:00:00-05:00',
#             'title': 'Test Event 3 - Big Tech',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-3/',
#         }, {
#             'publishing_date': '2020-06-15T08:00:00-04:00',
#             'title': 'Test Event 14',
#             'topics': ['Test Topic 1'],
#             'url': '/events/event-14/',
#         }])
