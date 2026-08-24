import base64
from datetime import datetime, timedelta, timezone as datetime_timezone
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.utils import timezone
from home.models import HomePage, Think7HomePage
from types import SimpleNamespace
from wagtail.test.utils import WagtailPageTestCase

from .models import EventListPage, EventPage, EventRegistrationReportPage
from .email_rendering import render_streamfield_email_html

from unittest.mock import patch


def test_owner():
    from django.contrib.auth import get_user_model

    user, _ = get_user_model().objects.get_or_create(
        username="events-test-owner",
        defaults={"email": "events-test-owner@example.com"},
    )
    return user


class EventCalendarTemplateTests(SimpleTestCase):
    def test_event_hero_does_not_render_add_to_calendar(self):
        class EmptyTopics:
            def all(self):
                return []

        html = render_to_string(
            "includes/heroes/hero_event.html",
            {
                "topics": EmptyTopics(),
                "title": "Template Event",
                "date": datetime(2030, 1, 1, 13, 0, tzinfo=datetime_timezone.utc),
                "end_date": datetime(2030, 1, 1, 14, 0, tzinfo=datetime_timezone.utc),
                "event_type": "Panel Discussion",
                "event_access": "Public",
                "authors": [],
                "author_count": 0,
                "registration_url": "https://example.com/register",
                "time_zone": "America/Toronto",
                "time_zone_label": "EST (UTC-05:00)",
                "is_past": False,
            },
        )

        self.assertIn("Register Now", html)
        self.assertNotIn("Add to Calendar", html)
        self.assertNotIn("/events/feed.ics", html)

    def test_add_to_calendar_include_renders_calendar_links(self):
        event = SimpleNamespace(
            id=123,
            title="Template Event",
            publishing_date=datetime(2030, 1, 1, 13, 0, tzinfo=datetime_timezone.utc),
            event_end=datetime(2030, 1, 1, 14, 0, tzinfo=datetime_timezone.utc),
            time_zone="America/Toronto",
            full_url="https://www.cigionline.org/events/template-event/",
            url="/events/template-event/",
        )

        html = render_to_string("events/includes/add_to_calendar.html", {"event": event})

        self.assertIn("Add to Calendar", html)
        self.assertIn("calendar/render", html)
        self.assertIn("/events/feed.ics?id=123", html)


class EmailCampaignAttachmentTests(SimpleTestCase):
    def test_attach_campaign_attachment_adds_wagtail_document_to_sendgrid_message(self):
        from sendgrid.helpers.mail import Mail

        from events.emailing import _attach_campaign_attachment

        class DummyFile:
            name = "event-campaigns/agenda.pdf"

            def __init__(self):
                self.opened = False
                self.closed = False

            def open(self, mode):
                self.opened = mode == "rb"

            def read(self):
                return b"%PDF-1.4"

            def close(self):
                self.closed = True

        dummy_file = DummyFile()
        document = SimpleNamespace(file=dummy_file, title="Agenda")
        message = Mail(
            from_email="events@example.com",
            to_emails="recipient@example.com",
            subject="Campaign",
            plain_text_content="Body",
        )

        _attach_campaign_attachment(message, document)

        attachment = message.get()["attachments"][0]
        self.assertTrue(dummy_file.opened)
        self.assertTrue(dummy_file.closed)
        self.assertEqual(attachment["content"], base64.b64encode(b"%PDF-1.4").decode())
        self.assertEqual(attachment["filename"], "agenda.pdf")
        self.assertEqual(attachment["type"], "application/pdf")
        self.assertEqual(attachment["disposition"], "attachment")


class DuplicateRegistrationTests(TestCase):
    """Duplicate email registrations should not create multiple active rows."""

    @patch("events.utils.verify_turnstile_token", return_value=True)
    @patch("events.emailing.send_duplicate_registration_manage_email")
    def test_duplicate_registration_does_not_create_second_registrant(self, send_mock, _turnstile_mock):
        from events.models import EventPage, RegistrationType, RegistrationFormTemplate, Registrant
        from wagtail.models import Site

        # Minimal Site/Page setup so the EventPage route can resolve.
        root = Site.objects.get(is_default_site=True).root_page
        event = EventPage(
            title="Dup Test Event",
            registration_open=True,
            publishing_date=timezone.now(),
            owner=test_owner(),
        )
        root.add_child(instance=event)
        event.save_revision(user=test_owner()).publish()
        event.registration_form_template = RegistrationFormTemplate.objects.create(title="Dup Test Template")
        event.save(update_fields=["registration_form_template"])

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

    @patch("events.utils.verify_turnstile_token", return_value=True)
    @patch("events.emailing.send_confirmation_email")
    def test_duplicate_registration_allows_if_cancelled(self, send_mock, _turnstile_mock):
        from events.models import EventPage, RegistrationType, RegistrationFormTemplate, Registrant
        from wagtail.models import Site

        root = Site.objects.get(is_default_site=True).root_page
        event = EventPage(
            title="Dup Cancelled Event",
            registration_open=True,
            publishing_date=timezone.now(),
            owner=test_owner(),
        )
        root.add_child(instance=event)
        event.save_revision(user=test_owner()).publish()
        event.registration_form_template = RegistrationFormTemplate.objects.create(title="Dup Cancelled Template")
        event.save(update_fields=["registration_form_template"])

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
            {EventRegistrationReportPage},
        )


class GuestRegistrationQuestionExclusionTests(TestCase):
    def test_exclude_from_guest_forms_omits_field_for_guests(self):
        from wagtail.models import Site
        from events.models import EventPage, RegistrationType, RegistrationFormTemplate, RegistrationFormField
        from events.guest_registration import build_primary_and_guest_forms

        root = Site.objects.get(is_default_site=True).root_page
        event = EventPage(title="Guest Exclusion Event", publishing_date=timezone.now(), owner=test_owner())
        root.add_child(instance=event)
        event.save_revision(user=test_owner()).publish()

        tmpl = RegistrationFormTemplate.objects.create(title="Guest Exclusion Template")
        event.registration_form_template = tmpl
        event.save(update_fields=["registration_form_template"])

        # Create a question that should NOT appear for guest registrants.
        RegistrationFormField.objects.create(
            template=tmpl,
            label="Primary-only question",
            field_type="singleline",
            required=False,
            sort_order=0,
            exclude_from_guest_forms=True,
        )

        reg_type = RegistrationType.objects.create(
            event=event,
            name="General",
            slug="general",
            sort_order=0,
            is_public=True,
            allow_group_registrations=True,
            max_guest_registrations=2,
        )

        forms_obj = build_primary_and_guest_forms(event=event, reg_type=reg_type, invite=None)
        self.assertIn(
            "f_" + str(RegistrationFormField.objects.first().field_key),
            forms_obj.primary_form.fields,
        )

        self.assertIsNotNone(forms_obj.guest_formset)
        guest_form = forms_obj.guest_formset.forms[0]
        self.assertNotIn(
            "f_" + str(RegistrationFormField.objects.first().field_key),
            guest_form.fields,
        )


class RegistrationChoiceLimitTests(TestCase):
    def _event_with_limited_choice(self, *, field_type="radio", limit=1, allow_groups=False):
        from wagtail.models import Site
        from events.models import EventPage, RegistrationType, RegistrationFormTemplate, RegistrationFormField

        root = Site.objects.get(is_default_site=True).root_page
        event = EventPage(
            title="Choice Limit Event",
            registration_open=True,
            publishing_date=timezone.now(),
        )
        root.add_child(instance=event)

        tmpl = RegistrationFormTemplate.objects.create(
            title=f"Choice Limit Template {field_type} {RegistrationFormTemplate.objects.count()}"
        )
        event.registration_form_template = tmpl
        event.save(update_fields=["registration_form_template"])

        reg_type = RegistrationType.objects.create(
            event=event,
            name="General",
            slug="general",
            sort_order=0,
            is_public=True,
            allow_group_registrations=allow_groups,
            max_guest_registrations=2,
        )
        field = RegistrationFormField.objects.create(
            template=tmpl,
            label="Session",
            field_type=field_type,
            choices="Workshop A\nWorkshop B",
            choice_limits=f"Workshop A | {limit}",
            required=False,
            sort_order=0,
        )
        return event, reg_type, field

    def test_choice_limits_model_validation_rejects_bad_mapping(self):
        from django.core.exceptions import ValidationError
        from events.models import RegistrationFormField, RegistrationFormTemplate

        tmpl = RegistrationFormTemplate.objects.create(title="Validation Template")
        field = RegistrationFormField(
            template=tmpl,
            label="Name",
            field_type="singleline",
            choices="Workshop A",
            choice_limits="Workshop A | 1",
        )

        with self.assertRaises(ValidationError):
            field.full_clean()

        field.field_type = "radio"
        field.choice_limits = "Missing | 1\nWorkshop A | nope\nWorkshop A | 2"
        with self.assertRaises(ValidationError):
            field.full_clean()

    def test_sold_out_choice_is_disabled_and_rejected(self):
        from events.forms import build_dynamic_form
        from events.models import Registrant

        event, reg_type, field = self._event_with_limited_choice()
        key = f"f_{field.field_key}"
        Registrant.objects.create(
            event=event,
            registration_type=reg_type,
            email="taken@example.com",
            answers={key: "Workshop A"},
            status=Registrant.Status.CONFIRMED,
        )

        form_class = build_dynamic_form(event, reg_type)
        html = str(form_class()[key])
        self.assertIn("disabled", html)
        self.assertIn("Workshop A (Sold out)", html)

        form = form_class(
            data={
                "first_name": "Test",
                "last_name": "User",
                "email": "test@example.com",
                "website": "",
                key: "Workshop A",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn(key, form.errors)

    def test_sold_out_dropdown_choice_is_disabled_and_rejected(self):
        from events.forms import build_dynamic_form
        from events.models import Registrant

        event, reg_type, field = self._event_with_limited_choice(field_type="dropdown")
        key = f"f_{field.field_key}"
        Registrant.objects.create(
            event=event,
            registration_type=reg_type,
            email="taken@example.com",
            answers={key: "Workshop A"},
            status=Registrant.Status.CONFIRMED,
        )

        form_class = build_dynamic_form(event, reg_type)
        html = str(form_class()[key])
        self.assertIn("disabled", html)
        self.assertIn("Workshop A (Sold out)", html)

        form = form_class(
            data={
                "first_name": "Test",
                "last_name": "User",
                "email": "test@example.com",
                "website": "",
                key: "Workshop A",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn(key, form.errors)

    def test_checkboxes_allow_available_choice_and_reject_sold_out_choice(self):
        from events.forms import build_dynamic_form
        from events.models import Registrant

        event, reg_type, field = self._event_with_limited_choice(field_type="checkboxes")
        key = f"f_{field.field_key}"
        Registrant.objects.create(
            event=event,
            registration_type=reg_type,
            email="taken@example.com",
            answers={key: ["Workshop A"]},
            status=Registrant.Status.CONFIRMED,
        )

        form_class = build_dynamic_form(event, reg_type)
        available_form = form_class(
            data={
                "first_name": "Test",
                "last_name": "User",
                "email": "test@example.com",
                "website": "",
                key: ["Workshop B"],
            }
        )
        self.assertTrue(available_form.is_valid(), available_form.errors)

        sold_out_form = form_class(
            data={
                "first_name": "Test",
                "last_name": "User",
                "email": "test@example.com",
                "website": "",
                key: ["Workshop A"],
            }
        )
        self.assertFalse(sold_out_form.is_valid())
        self.assertIn(key, sold_out_form.errors)

    def test_conditional_dropdown_choice_limits_selected_value(self):
        from events.forms import build_dynamic_form
        from events.models import Registrant

        event, reg_type, field = self._event_with_limited_choice(field_type="conditional_dropdown_other")
        key = f"f_{field.field_key}"
        other_key = f"{key}__other"
        Registrant.objects.create(
            event=event,
            registration_type=reg_type,
            email="taken@example.com",
            answers={key: "Workshop A", other_key: ""},
            status=Registrant.Status.CONFIRMED,
        )

        form_class = build_dynamic_form(event, reg_type)
        form = form_class(
            data={
                "first_name": "Test",
                "last_name": "User",
                "email": "test@example.com",
                "website": "",
                key: "Workshop A",
                other_key: "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn(key, form.errors)

    def test_current_registrant_can_keep_full_choice(self):
        from events.forms import build_dynamic_form
        from events.models import Registrant

        event, reg_type, field = self._event_with_limited_choice()
        key = f"f_{field.field_key}"
        registrant = Registrant.objects.create(
            event=event,
            registration_type=reg_type,
            email="holder@example.com",
            first_name="Existing",
            last_name="Holder",
            answers={key: "Workshop A"},
            status=Registrant.Status.CONFIRMED,
        )

        form_class = build_dynamic_form(event, reg_type, require_email=False, current_registrant=registrant)
        form = form_class(
            data={
                "first_name": "Existing",
                "last_name": "Holder",
                "website": "",
                key: "Workshop A",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_current_registrant_cannot_switch_into_different_full_choice(self):
        from events.forms import build_dynamic_form
        from events.models import Registrant

        event, reg_type, field = self._event_with_limited_choice()
        field.choice_limits = "Workshop A | 1\nWorkshop B | 1"
        field.save(update_fields=["choice_limits"])
        key = f"f_{field.field_key}"
        registrant = Registrant.objects.create(
            event=event,
            registration_type=reg_type,
            email="holder-a@example.com",
            first_name="Holder",
            last_name="A",
            answers={key: "Workshop A"},
            status=Registrant.Status.CONFIRMED,
        )
        Registrant.objects.create(
            event=event,
            registration_type=reg_type,
            email="holder-b@example.com",
            answers={key: "Workshop B"},
            status=Registrant.Status.CONFIRMED,
        )

        form_class = build_dynamic_form(event, reg_type, require_email=False, current_registrant=registrant)
        form = form_class(
            data={
                "first_name": "Holder",
                "last_name": "A",
                "website": "",
                key: "Workshop B",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn(key, form.errors)

    def test_pending_and_waitlisted_registrants_consume_choice_limit(self):
        from events.forms import build_dynamic_form
        from events.models import Registrant

        event, reg_type, field = self._event_with_limited_choice(limit=2)
        key = f"f_{field.field_key}"
        for status, email in (
            (Registrant.Status.PENDING, "pending@example.com"),
            (Registrant.Status.WAITLISTED, "waitlisted@example.com"),
        ):
            Registrant.objects.create(
                event=event,
                registration_type=reg_type,
                email=email,
                answers={key: "Workshop A"},
                status=status,
            )

        form_class = build_dynamic_form(event, reg_type)
        form = form_class(
            data={
                "first_name": "New",
                "last_name": "User",
                "email": "new@example.com",
                "website": "",
                key: "Workshop A",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn(key, form.errors)

    def test_choice_summary_counts_active_registrants_and_limits(self):
        from events.models import Registrant
        from events.reporting import build_choice_summary_rows

        event, reg_type, field = self._event_with_limited_choice(field_type="checkboxes", limit=3)
        key = f"f_{field.field_key}"
        for status, email, answers in (
            (Registrant.Status.PENDING, "pending@example.com", ["Workshop A", "Workshop B"]),
            (Registrant.Status.CONFIRMED, "confirmed@example.com", ["Workshop A"]),
            (Registrant.Status.WAITLISTED, "waitlisted@example.com", ["Workshop B"]),
            (Registrant.Status.CANCELLED, "cancelled@example.com", ["Workshop A"]),
        ):
            Registrant.objects.create(
                event=event,
                registration_type=reg_type,
                email=email,
                answers={key: answers},
                status=status,
            )

        rows = build_choice_summary_rows(event)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["label"], "Session")
        options = {option["label"]: option for option in rows[0]["options"]}
        self.assertEqual(options["Workshop A"]["count"], 2)
        self.assertEqual(options["Workshop A"]["limit"], 3)
        self.assertEqual(options["Workshop B"]["count"], 2)
        self.assertIsNone(options["Workshop B"]["limit"])

    def test_cancelled_registrant_does_not_consume_choice_limit(self):
        from events.forms import build_dynamic_form
        from events.models import Registrant

        event, reg_type, field = self._event_with_limited_choice()
        key = f"f_{field.field_key}"
        Registrant.objects.create(
            event=event,
            registration_type=reg_type,
            email="cancelled@example.com",
            answers={key: "Workshop A"},
            status=Registrant.Status.CANCELLED,
        )

        form_class = build_dynamic_form(event, reg_type)
        form = form_class(
            data={
                "first_name": "New",
                "last_name": "User",
                "email": "new@example.com",
                "website": "",
                key: "Workshop A",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_group_registration_cannot_exceed_remaining_choice_limit(self):
        from events.forms import validate_choice_limits

        event, reg_type, field = self._event_with_limited_choice(limit=1, allow_groups=True)
        key = f"f_{field.field_key}"

        errors = validate_choice_limits(
            event,
            reg_type,
            [
                {key: "Workshop A"},
                {key: "Workshop A"},
            ],
        )

        self.assertEqual(errors[key], '"Workshop A" is sold out.')


class RegistrationRichTextBlockTests(TestCase):
    def _event_with_template(self):
        from wagtail.models import Site
        from django.contrib.auth import get_user_model
        from events.models import EventPage, RegistrationType, RegistrationFormTemplate

        root = Site.objects.get(is_default_site=True).root_page
        owner = get_user_model().objects.create_user(
            username="richtext-owner",
            email="owner@example.com",
            password="password",
        )
        event = EventPage(
            title="Rich Text Event",
            registration_open=True,
            publishing_date=timezone.now(),
            owner=owner,
        )
        root.add_child(instance=event)
        event.save_revision(user=owner).publish()

        tmpl = RegistrationFormTemplate.objects.create(title="Rich Text Template")
        event.registration_form_template = tmpl
        event.save(update_fields=["registration_form_template"])

        reg_type = RegistrationType.objects.create(
            event=event,
            name="General",
            slug="general",
            sort_order=0,
            is_public=True,
            allow_group_registrations=True,
            max_guest_registrations=2,
        )
        return event, reg_type, tmpl

    def test_rich_text_block_renders_on_registration_form_between_fields(self):
        from events.models import RegistrationFormField

        event, reg_type, tmpl = self._event_with_template()
        RegistrationFormField.objects.create(
            template=tmpl,
            label="Organization",
            field_type="singleline",
            required=False,
            sort_order=0,
        )
        RegistrationFormField.objects.create(
            template=tmpl,
            label="Arrival instructions",
            field_type="rich_text",
            rich_text="<p>Please arrive early.</p>",
            sort_order=1,
        )
        RegistrationFormField.objects.create(
            template=tmpl,
            label="Role",
            field_type="singleline",
            required=False,
            sort_order=2,
        )

        resp = self.client.get(f"{event.url}register/type/{reg_type.slug}/")

        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        self.assertIn("<p>Please arrive early.</p>", html)
        self.assertLess(html.index("Organization"), html.index("Please arrive early."))
        self.assertLess(html.index("Please arrive early."), html.index("Role"))

    def test_rich_text_block_is_not_form_field_or_saved_answer_or_report_output(self):
        from events.emailing import _render_registrant_answers
        from events.forms import build_dynamic_form
        from events.models import RegistrationFormField
        from events.reporting import build_answer_columns, registrants_csv_response
        from events.utils import save_registrant_from_form

        event, reg_type, tmpl = self._event_with_template()
        answer_field = RegistrationFormField.objects.create(
            template=tmpl,
            label="Organization",
            field_type="singleline",
            required=False,
            sort_order=0,
        )
        rich_block = RegistrationFormField.objects.create(
            template=tmpl,
            label="Arrival instructions",
            field_type="rich_text",
            rich_text="<p>Please arrive early.</p>",
            sort_order=1,
        )

        form_class = build_dynamic_form(event, reg_type)
        rich_key = f"f_{rich_block.field_key}"
        answer_key = f"f_{answer_field.field_key}"
        self.assertNotIn(rich_key, form_class.base_fields)

        form = form_class(
            data={
                "first_name": "Test",
                "last_name": "Registrant",
                "email": "test@example.com",
                "website": "",
                answer_key: "CIGI",
                rich_key: "posted junk",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertNotIn(rich_key, form.cleaned_data)

        form.cleaned_data[rich_key] = "posted junk"
        registrant = save_registrant_from_form(event, reg_type, form)
        self.assertEqual(registrant.answers, {answer_key: "CIGI"})

        columns = build_answer_columns(event)
        self.assertEqual([column.label for column in columns], ["Organization"])

        csv_resp = registrants_csv_response(
            request=RequestFactory().get("/"),
            event=event,
            registrants_qs=event.registrants.select_related("registration_type", "invite"),
            filename_prefix="rich-text",
        )
        csv_text = csv_resp.content.decode("utf-8-sig")
        self.assertIn("Organization", csv_text)
        self.assertNotIn("Arrival instructions", csv_text)
        self.assertNotIn("Please arrive early", csv_text)

        answers_html, answers_text = _render_registrant_answers(registrant)
        self.assertIn("Organization", answers_text)
        self.assertNotIn("Arrival instructions", answers_text)
        self.assertNotIn("Please arrive early", answers_html)

    def test_rich_text_block_respects_guest_exclusion_in_layout(self):
        from events.models import RegistrationFormField
        from events.guest_registration import build_primary_and_guest_forms

        event, reg_type, tmpl = self._event_with_template()
        RegistrationFormField.objects.create(
            template=tmpl,
            label="Primary instructions",
            field_type="rich_text",
            rich_text="<p>Primary only.</p>",
            sort_order=0,
            exclude_from_guest_forms=True,
        )

        forms_obj = build_primary_and_guest_forms(event=event, reg_type=reg_type, invite=None)
        primary_items = forms_obj.primary_form.layout_items()
        guest_items = forms_obj.guest_formset.forms[0].layout_items()

        self.assertIn("Primary only.", str(primary_items[0]["content"]))
        self.assertEqual(guest_items, [])


class GroupRegistrationConfirmTests(TestCase):
    @patch("events.utils.verify_turnstile_token", return_value=True)
    @patch("events.emailing.send_group_confirmation_email")
    def test_group_registration_immediately_confirms_and_sends_confirmation_email(self, send_mock, _turnstile_mock):
        from wagtail.models import Site
        from events.models import EventPage, RegistrationType, RegistrationFormTemplate

        root = Site.objects.get(is_default_site=True).root_page
        event = EventPage(
            title="Group Confirm Event",
            registration_open=True,
            publishing_date=timezone.now(),
            owner=test_owner(),
        )
        root.add_child(instance=event)
        event.save_revision(user=test_owner()).publish()

        tmpl = RegistrationFormTemplate.objects.create(title="Group Template")
        event.registration_form_template = tmpl
        event.save(update_fields=["registration_form_template"])

        reg_type = RegistrationType.objects.create(
            event=event,
            name="General",
            slug="general",
            sort_order=0,
            is_public=True,
            allow_group_registrations=True,
            max_guest_registrations=2,
        )

        resp = self.client.post(
            f"{event.url}register/type/{reg_type.slug}/",
            data={
                "first_name": "Primary",
                "last_name": "User",
                "email": "primary@example.com",
                "website": "",
                # One guest
                "guests-TOTAL_FORMS": "1",
                "guests-INITIAL_FORMS": "0",
                "guests-MIN_NUM_FORMS": "0",
                "guests-MAX_NUM_FORMS": "2",
                "guests-0-first_name": "Guest",
                "guests-0-last_name": "One",
            },
        )

        self.assertEqual(resp.status_code, 302)
        self.assertIn("register/result/?s=", resp["Location"])
        self.assertNotIn("s=pending", resp["Location"])
        self.assertTrue(send_mock.called)

        from events.models import Registrant

        statuses = list(Registrant.objects.filter(event=event).values_list("status", flat=True))
        # Primary + guest should be immediately confirmed or waitlisted (not pending).
        self.assertTrue(statuses)
        self.assertTrue(all(s in (Registrant.Status.CONFIRMED, Registrant.Status.WAITLISTED) for s in statuses))


class RegistrationTypeCloseDateTests(TestCase):
    def test_expired_registration_type_is_hidden_from_entry_flow(self):
        from wagtail.models import Site
        from events.models import EventPage, RegistrationType

        root = Site.objects.get(is_default_site=True).root_page
        event = EventPage(
            title="Close Date Event",
            registration_open=True,
            publishing_date=timezone.now(),
            owner=test_owner(),
        )
        root.add_child(instance=event)
        event.save_revision(user=test_owner()).publish()

        RegistrationType.objects.create(
            event=event,
            name="Closed",
            slug="closed",
            sort_order=0,
            is_public=True,
            close_date=timezone.now() - timedelta(days=1),
        )
        open_type = RegistrationType.objects.create(
            event=event,
            name="Open",
            slug="open",
            sort_order=1,
            is_public=True,
            close_date=timezone.now() + timedelta(days=1),
        )

        resp = self.client.get(f"{event.url}register/")

        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp["Location"].endswith(f"register/type/{open_type.slug}/"))

    def test_expired_registration_type_direct_url_is_unavailable(self):
        from wagtail.models import Site
        from events.models import EventPage, RegistrationType, Registrant

        root = Site.objects.get(is_default_site=True).root_page
        event = EventPage(
            title="Closed Direct Event",
            registration_open=True,
            publishing_date=timezone.now(),
            owner=test_owner(),
        )
        root.add_child(instance=event)
        event.save_revision(user=test_owner()).publish()

        reg_type = RegistrationType.objects.create(
            event=event,
            name="Closed",
            slug="closed",
            sort_order=0,
            is_public=True,
            close_date=timezone.now() - timedelta(days=1),
        )

        resp = self.client.post(
            f"{event.url}register/type/{reg_type.slug}/",
            data={
                "first_name": "Closed",
                "last_name": "Registrant",
                "email": "closed@example.com",
                "website": "",
            },
        )

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "events/registration_no_types.html")
        self.assertFalse(Registrant.objects.filter(event=event).exists())


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

    def test_events_api_excludes_events_not_added_to_calendar(self):
        EventPage.objects.filter(title="Test Event 2").update(add_to_calendar=False)

        response = self.get_api_response(1, 2020)

        self.assertEqual(response['meta']['total_count'], 2)
        self.assertNotIn("Test Event 2", [item["title"] for item in response["items"]])

    def test_events_api_is_not_cached(self):
        response = self.client.get('/api/events/?month=1&year=2020')

        self.assertIn("no-store", response.headers["Cache-Control"])


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

    def test_registrant_answers_merge_variable_renders(self):
        from wagtail.models import Site
        from events.models import EventPage, RegistrationType, Registrant, EmailTemplate
        from events.email_rendering import render_streamfield_email_html

        root = Site.objects.get(is_default_site=True).root_page
        event = EventPage(title="Answers Event", publishing_date=timezone.now(), owner=test_owner())
        root.add_child(instance=event)
        event.save_revision(user=test_owner()).publish()

        reg_type = RegistrationType(event=event, name="General", slug="general", sort_order=0, is_public=True)
        reg_type.save()

        registrant = Registrant.objects.create(
            event=event,
            registration_type=reg_type,
            email="a@example.com",
            first_name="A",
            last_name="B",
            answers={"f_company": "CIGI", "f_role": "Researcher"},
        )

        tmpl = EmailTemplate(title="T", subject="S", body=[{"type": "answers", "value": None}])

        from events.emailing import _render_registrant_answers

        answers_html, answers_text = _render_registrant_answers(registrant)

        html, _text = render_streamfield_email_html(
            template_obj=tmpl,
            ctx={
                "event": event,
                "registrant": registrant,
                "registration_type": reg_type,
                "confirmed": True,
                "manage_url": "https://example.com/manage",
                "registrant_answers_html": answers_html,
                "registrant_answers_text": answers_text,
            },
        )

        self.assertIn("Registration details", html)
        self.assertIn("CIGI", html)

    def test_registrant_answers_does_not_treat_f_uuid_as_builtin_email(self):
        """If an answer label shows a UUID, it can't be the built-in Registrant.email.

        Built-in identity fields are stored on the Registrant model and are excluded
        from answers output when present under literal keys like 'email'. Dynamic
        fields are stored under keys like f_<uuid>.
        """

        import uuid

        from wagtail.models import Site
        from events.models import EventPage, RegistrationType, Registrant
        from events.emailing import _render_registrant_answers

        root = Site.objects.get(is_default_site=True).root_page
        event = EventPage(title="Answers UUID Event", publishing_date=timezone.now(), owner=test_owner())
        root.add_child(instance=event)
        event.save_revision(user=test_owner()).publish()

        reg_type = RegistrationType(event=event, name="General", slug="general", sort_order=0, is_public=True)
        reg_type.save()

        fake_field_key = uuid.uuid4()
        registrant = Registrant.objects.create(
            event=event,
            registration_type=reg_type,
            email="built-in@example.com",
            first_name="A",
            last_name="B",
            answers={
                "email": "should-not-appear@example.com",
                f"f_{fake_field_key}": "dynamic@example.com",
                "f_company": "CIGI",
            },
        )

        _html, text = _render_registrant_answers(registrant)

        # Literal 'email' is treated as identity field and excluded.
        self.assertNotIn("should-not-appear@example.com", text)
        # Unresolvable dynamic UUID-style key is rendered under a neutral fallback label.
        self.assertIn("dynamic@example.com", text)
        self.assertNotIn(str(fake_field_key), text)
        self.assertIn("Additional question", text)
        # Other non-uuid keys still render.
        self.assertIn("CIGI", text)

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
