from unittest.mock import Mock, patch

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase, TestCase
from mailchimp_marketing.api_client import ApiClientError
from wagtail.test.utils import WagtailPageTestCase

from subscribe.models import SubscribePage, TFGBVSubscribeForm, TFGBVSubscribePage
from subscribe.views import DphSubscribeForm, subscribe_dph
from home.models import HomePage


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
    def test_get_renders_signup_page_with_email_prefilled(self, mock_render):
        response = subscribe_dph(self.factory.get('/subscribe_dph?email=reader@example.com'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_render.call_args.args[1], 'themes/dph/subscribe_page.html')
        self.assertEqual(mock_render.call_args.args[2]['form'].initial['email'], 'reader@example.com')

    @patch('subscribe.views.render', return_value=HttpResponse())
    @patch('subscribe.views.MailchimpMarketing.Client')
    def test_requires_consent(self, mock_client, mock_render):
        post_data = self.valid_post_data.copy()
        post_data.pop('consent')

        response = subscribe_dph(self.factory.post('/subscribe_dph', post_data))

        self.assertEqual(response.status_code, 200)
        self.assertIn('consent', mock_render.call_args.args[2]['form'].errors)
        mock_client.assert_not_called()

    @patch('subscribe.views.render', return_value=HttpResponse())
    @patch('subscribe.views.MailchimpMarketing.Client')
    def test_sends_profile_and_consent_to_mailchimp(self, mock_client, mock_render):
        mailchimp = mock_client.return_value
        mailchimp.lists.get_list_member.side_effect = ApiClientError('404', 404)
        mailchimp.lists.set_list_member.return_value = {'status': 'subscribed'}

        with (
            patch('subscribe.views.api_key', 'key'),
            patch('subscribe.views.server', 'us1'),
            patch('subscribe.views.list_id', 'list-id'),
        ):
            response = subscribe_dph(self.factory.post('/subscribe_dph', self.valid_post_data))

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
    def test_existing_subscriber_is_not_updated(self, mock_client, mock_render):
        mailchimp = mock_client.return_value
        mailchimp.lists.get_list_member.return_value = {'status': 'subscribed'}

        with (
            patch('subscribe.views.api_key', 'key'),
            patch('subscribe.views.server', 'us1'),
            patch('subscribe.views.list_id', 'list-id'),
        ):
            subscribe_dph(self.factory.post('/subscribe_dph', self.valid_post_data))

        mailchimp.lists.set_list_member.assert_not_called()
        self.assertEqual(mock_render.call_args.args[2]['status'], 'subscribed')

    @patch('subscribe.views.render', return_value=HttpResponse())
    @patch('subscribe.views.MailchimpMarketing.Client')
    def test_mailchimp_error_renders_error_status(self, mock_client, mock_render):
        mailchimp = mock_client.return_value
        mailchimp.lists.get_list_member.side_effect = ApiClientError('404', 404)
        mailchimp.lists.set_list_member.side_effect = ApiClientError('Invalid Resource', 400)

        with (
            patch('subscribe.views.api_key', 'key'),
            patch('subscribe.views.server', 'us1'),
            patch('subscribe.views.list_id', 'list-id'),
        ):
            subscribe_dph(self.factory.post('/subscribe_dph', self.valid_post_data))

        self.assertEqual(mock_render.call_args.args[2]['status'], 'error')


class SubscribeDphTemplateTests(TestCase):
    def test_signup_page_uses_design_system_form(self):
        html = render_to_string('themes/dph/subscribe_page.html', {'form': DphSubscribeForm()})

        self.assertIn('ds-form', html)
        for name in ('email', 'first_name', 'last_name', 'job_title', 'company', 'country', 'consent'):
            self.assertIn(f'name="{name}"', html)

    def test_status_page_uses_dph_copy_and_social_link(self):
        html = render_to_string(
            'subscribe/subscribe_page_landing.html',
            {'status': 'subscribed_success', 'subscription_type': 'dph'},
        )

        self.assertIn('Digital Policy Hub', html)
        self.assertIn('Thank You for Subscribing', html)
        self.assertIn("Keep an eye on your inbox. We'll let you know", html)
        self.assertIn('digital-policy-hub-cigi', html)

    def test_dph_footer_links_to_signup_and_legacy_sidebar_links_to_application(self):
        footer = render_to_string('themes/dph/includes/footer.html')
        sidebar = render_to_string('themes/dph/includes/sidebar.html')

        self.assertIn('method="get"', footer)
        self.assertIn('name="email"', footer)
        self.assertIn('href="/careers/dph-call-for-applications-2027/"', sidebar)
        self.assertIn('Apply Now', sidebar)
        self.assertNotIn('id="mailing-list-button"', sidebar)


class SubscribePageTests(WagtailPageTestCase):
    def test_tfgbv_form_requires_affiliation_and_country(self):
        form = TFGBVSubscribeForm(data={
            'first_name': 'Ada',
            'last_name': 'Lovelace',
            'email': 'ada@example.com',
            'affiliation': 'CIGI',
            'location': 'CA',
            'consent': True,
        })

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(TFGBVSubscribePage().get_country(form), 'Canada')

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

    @patch('utils.security.verify_turnstile_token', return_value=False)
    def test_result_and_footer_include_current_social_destinations(self, _verify_turnstile):
        page = HomePage.objects.get().add_child(instance=SubscribePage(
            title='Subscribe', slug='subscribe-social-links'))
        page.save_revision().publish()

        response = self.client.post(page.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="ds-share-buttons__link"', count=6)
        for label in ('X', 'LinkedIn', 'YouTube', 'Instagram', 'Substack', 'Medium'):
            self.assertContains(response, f'aria-label="CIGI on {label}"')
        self.assertContains(response, 'aria-label="CIGI on Apple Podcasts"')
        self.assertContains(response, 'aria-label="CIGI on Spotify"')

    def test_apply_tag_includes_anniversary_tag(self):
        client = Mock()

        SubscribePage().apply_tag(
            client,
            'list-id',
            'subscriber-hash',
            extra_tags=['25 Anniversary'],
        )

        client.lists.update_list_member_tags.assert_called_once_with(
            'list-id',
            'subscriber-hash',
            {
                'tags': [
                    {'name': 'CIGI Weekly Newsletter', 'status': 'active'},
                    {'name': '25 Anniversary', 'status': 'active'},
                ],
            },
        )
