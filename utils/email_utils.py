from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail,
    Attachment,
    FileContent,
    FileName,
    FileType,
    Disposition,
)
import base64


def send_email_with_attachment(recipient, subject, body, uploaded_file):
    """Send an email with an attachment via SendGrid."""

    try:
        sg = SendGridAPIClient(settings.THINK7_SENDGRID_API_KEY)
        message = Mail(
            from_email='info@think7.org',
            to_emails=recipient,
            subject=subject,
            plain_text_content=body,
        )

        file_data = uploaded_file.read()
        encoded_file = base64.b64encode(file_data).decode()
        attachment = Attachment(
            FileContent(encoded_file),
            FileName(uploaded_file.name),
            FileType(uploaded_file.content_type),
            Disposition('attachment'),
        )
        message.attachment = attachment
        sg.send(message)
    except Exception as e:
        print(f'Error sending email: {str(e)}')


def send_email(recipient, subject, body):
    '''Send a simple email via SendGrid.'''

    try:
        sg = SendGridAPIClient(settings.THINK7_SENDGRID_API_KEY)
        message = Mail(
            from_email='info@think7.org',
            to_emails=recipient,
            subject=subject,
            plain_text_content=body,
        )
        sg.send(message)

    except Exception as e:
        print(f'Error sending email: {str(e)}')


def extract_errors_as_string(form_errors):
    return [str(error) for field_errors in form_errors.values() for error in field_errors]
