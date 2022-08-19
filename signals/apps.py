import requests
import json
import os
from wagtail.core.signals import page_published
from django.apps import AppConfig
from django.core.mail import EmailMultiAlternatives


def send_email(title, authors, page_owner):
    recipients = ['ywang@cigionline.org']  # hardcoded placeholder test recipients

    text_content = f"{title} By Author(s): {authors} Published By: {page_owner}"
    html_content = f"<p><i>{title}</i></p><p>By Author(s): {authors}</p><p>Published By: {page_owner}</p>"

    msg = EmailMultiAlternatives(
        "New Page Published",  # title
        text_content,  # body
        os.environ['DEFAULT_FROM_EMAIL'],  # from email
        recipients,  # to emails
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_to_slack(title, authors, page_owner):
    values = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"_{title}_ \n By Author(s): {authors} \n Published By: {page_owner}",
                }
            }
        ]
    }
    url = os.environ['SLACK_WEBHOOK_URL']  # hardcoded placeholder test channel

    if 'NOTIFICATION_OFF' in os.environ and not (os.environ['NOTIFICATION_OFF'].lower() == "true"):
        requests.post(url, json.dumps(values))


def instance_info(instance):
    title = instance.title
    authors = ', '.join([' '.join([author.author.first_name, author.author.last_name]) for author in instance.authors.all()])
    page_owner = instance.owner.username
    return title, authors, page_owner


# Let everyone know when a new page is published
def send_notifications(sender, **kwargs):
    instance = kwargs['instance']

    title, authors, page_owner = instance_info(instance)

    # wrap in try/except to not disrupt normal operations if a page is successfully published but email could not be sent
    try:
        send_to_slack(title, authors, page_owner)
        send_email(title, authors, page_owner)
    except Exception as e:
        print(e)


class SignalsConfig(AppConfig):
    name = 'signals'
    verbose_name = "Signals"

    def ready(self):
        from articles.models import ArticlePage, ArticleSeriesPage
        from publications.models import PublicationPage
        from multimedia.models import MultimediaPage

        page_published.connect(send_notifications, sender=ArticlePage)
        page_published.connect(send_notifications, sender=ArticleSeriesPage)
        page_published.connect(send_notifications, sender=PublicationPage)
        page_published.connect(send_notifications, sender=MultimediaPage)
