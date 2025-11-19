from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_facility_rental_email(request, recipients: list[str], form_data: dict):
    """
    Uses SendGrid to email the parsed form data to recipients.
    """
    api_key = settings.SENDGRID_API_KEY
    if not api_key:
        raise RuntimeError("SENDGRID_API_KEY is not configured")

    subject = f"[Rental Inquiry] {form_data.get('start_date').strftime('%B %-d, %Y')} — {form_data.get('company')} - {form_data.get('event_title')} - {form_data.get('first_name')} {form_data.get('last_name')}"

    html_body = render_to_string("core/email/facility_rental_notification.html", {"data": form_data})
    text_body = strip_tags(html_body)

    message = Mail(
        from_email=settings.SENDGRID_FROM_EMAIL_RENTALS,
        to_emails=recipients,
        subject=subject,
        html_content=html_body,
        plain_text_content=text_body,
    )

    sg = SendGridAPIClient(api_key)
    response = sg.send(message)
    if response.status_code != 202:
        raise RuntimeError(f"Failed to send email, status code: {response.status_code}")
    return response


def send_facility_rental_confirmation_email(form_data):
    """
    Send a confirmation email back to the submitter.
    """

    api_key = settings.SENDGRID_API_KEY
    if not api_key:
        raise RuntimeError("SENDGRID_API_KEY not configured")

    subject = "CIGI Event Rental Inquiry - Submission Confirmation"
    html_body = render_to_string(
        "core/email/facility_rental_confirmation.html", {"data": form_data}
    )
    text_body = strip_tags(html_body)

    message = Mail(
        from_email=settings.SENDGRID_FROM_EMAIL_RENTALS,
        to_emails=form_data["email"],
        subject=subject,
        html_content=html_body,
        plain_text_content=text_body,
    )

    sg = SendGridAPIClient(api_key)
    sg.send(message)
