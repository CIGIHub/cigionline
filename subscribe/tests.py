from unittest.mock import patch

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase, TestCase
from mailchimp_marketing.api_client import ApiClientError
from wagtail.test.utils import WagtailPageTestCase

from home.models import HomePage
from subscribe.models import SubscribePage
from subscribe.views import DphSubscribeForm, subscribe_dph


class SubscribeDphTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.valid_post_data = {
            'email': 'reader@example.com',
            'first_name': 'Ada',
            'last_name': 'Lovelace',
            'job_title': 'Researcher',
            'company': 'Analytical Engines Inc.',
            'country': 'CA',
            'consent': 'on',
        }

    @patch('subscribe.views.render', return_value=HttpResponse())
    def test_subscribe_dph_get_renders_signup_page(self, mock_render):
        request = self.factory.get('/subscribe_dph')

        response = subscribe_dph(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_render.call_args.args[1], 'themes/dph/subscribe_page.html')

    @patch('subscribe.views.render', return_value=HttpResponse())
    @patch('subscribe.views.MailchimpMarketing.Client')
    def test_subscribe_dph_requires_consent(self, mock_client, mock_render):
        post_data = self.valid_post_data.copy()
        post_data.pop('consent')
        request = self.factory.post('/subscribe_dph', post_data)

        response = subscribe_dph(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_render.call_args.args[1], 'themes/dph/subscribe_page.html')
        self.assertIn('consent', mock_render.call_args.args[2]['form'].errors)
        mock_client.assert_not_called()

    @patch('subscribe.views.render', return_value=HttpResponse())
    @patch('subscribe.views.MailchimpMarketing.Client')
    def test_subscribe_dph_sends_consent_to_mailchimp(self, mock_client, mock_render):
        mailchimp = mock_client.return_value
        mailchimp.lists.get_list_member.side_effect = ApiClientError('404', 404)
        mailchimp.lists.set_list_member.return_value = {'status': 'subscribed'}
        request = self.factory.post('/subscribe_dph', self.valid_post_data)

        with (
            patch('subscribe.views.api_key', 'key'),
            patch('subscribe.views.server', 'us1'),
            patch('subscribe.views.list_id', 'list-id'),
        ):
            response = subscribe_dph(request)

        self.assertEqual(response.status_code, 200)
        mailchimp.lists.set_list_member.assert_called_once_with(
            'list-id',
            'baa0f4114eafbdd39ce828d01b849ae6',
            {
                'email_address': 'reader@example.com',
                'status_if_new': 'subscribed',
                'merge_fields': {
                    'FNAME': 'Ada',
                    'LNAME': 'Lovelace',
                    'JOBTITLE': 'Researcher',
                    'COMPANY': 'Analytical Engines Inc.',
                    'COUNTRY': 'Canada',
                    'CONSENT': 'true',
                },
            },
        )
        self.assertEqual(mock_render.call_args.args[2]['status'], 'subscribed_success')

    @patch('subscribe.views.render', return_value=HttpResponse())
    @patch('subscribe.views.MailchimpMarketing.Client')
    def test_subscribe_dph_already_subscribed_keeps_subscribed_status(self, mock_client, mock_render):
        mailchimp = mock_client.return_value
        mailchimp.lists.get_list_member.return_value = {'status': 'subscribed'}
        request = self.factory.post('/subscribe_dph', self.valid_post_data)

        with (
            patch('subscribe.views.api_key', 'key'),
            patch('subscribe.views.server', 'us1'),
            patch('subscribe.views.list_id', 'list-id'),
        ):
            response = subscribe_dph(request)

        self.assertEqual(response.status_code, 200)
        mailchimp.lists.set_list_member.assert_not_called()
        self.assertEqual(mock_render.call_args.args[2]['status'], 'subscribed')

    @patch('subscribe.views.render', return_value=HttpResponse())
    @patch('subscribe.views.MailchimpMarketing.Client')
    def test_subscribe_dph_mailchimp_error_renders_error_status(self, mock_client, mock_render):
        mailchimp = mock_client.return_value
        mailchimp.lists.get_list_member.side_effect = ApiClientError('404', 404)
        mailchimp.lists.set_list_member.side_effect = ApiClientError('Invalid Resource', 400)
        request = self.factory.post('/subscribe_dph', self.valid_post_data)

        with (
            patch('subscribe.views.api_key', 'key'),
            patch('subscribe.views.server', 'us1'),
            patch('subscribe.views.list_id', 'list-id'),
        ):
            response = subscribe_dph(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_render.call_args.args[1], 'subscribe/subscribe_page_landing.html')
        self.assertEqual(mock_render.call_args.args[2]['status'], 'error')


class SubscribeLandingTemplateTests(TestCase):
    def test_dph_signup_page_renders_form_fields(self):
        html = render_to_string(
            'themes/dph/subscribe_page.html',
            {
                'form': DphSubscribeForm(),
            },
        )

        self.assertIn('/static/bundles/themeDPH.', html)
        self.assertIn('dph-basic-page', html)
        self.assertIn('name="email"', html)
        self.assertIn('name="first_name"', html)
        self.assertIn('name="last_name"', html)
        self.assertIn('name="job_title"', html)
        self.assertIn('name="company"', html)
        self.assertIn('name="country"', html)
        self.assertIn('name="consent"', html)

    def test_dph_status_page_gets_dph_styling_only_for_dph_flow(self):
        dph_html = render_to_string(
            'subscribe/subscribe_page_landing.html',
            {
                'status': 'subscribed_success',
                'subscription_type': 'dph',
            },
        )
        digital_finance_html = render_to_string(
            'subscribe/subscribe_page_landing.html',
            {
                'status': 'pending',
                'subscription_type': 'digital_finance',
            },
        )

        self.assertIn('/static/bundles/themeDPH.', dph_html)
        self.assertIn('dph-basic-page', dph_html)
        self.assertIn('Digital Policy Hub', dph_html)
        self.assertIn('Thank You for Subscribing', dph_html)
        self.assertIn("Keep an eye on your inbox. We'll let you know about upcoming working papers, events and cohort announcements.", dph_html)
        self.assertIn('Stay connected on LinkedIn for more frequent updates.', dph_html)
        self.assertIn('https://www.linkedin.com/showcase/digital-policy-hub-cigi/?utm_source=cigionline.org&utm_medium=referral&utm_campaign=dph_subscribe_success', dph_html)
        self.assertNotIn('/static/bundles/themeDPH.', digital_finance_html)
        self.assertNotIn('dph-basic-page', digital_finance_html)

    def test_dph_status_page_has_already_subscribed_message(self):
        html = render_to_string(
            'subscribe/subscribe_page_landing.html',
            {
                'status': 'subscribed',
                'subscription_type': 'dph',
            },
        )

        self.assertIn("You're already subscribed.", html)
        self.assertIn('Your email is already subscribed.', html)


class SubscribePageTests(WagtailPageTestCase):
    def test_subscribepage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            SubscribePage,
            {HomePage},
        )

    def test_subscribepage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            SubscribePage,
            {},
        )
