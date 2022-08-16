import requests
import json
import os
from wagtail.core.signals import page_published
from django.apps import AppConfig
from django.core.mail import send_mail


def send_email(instance):
    body = "_%s_ \n By Author(s): name, name \n Published By: %s " % (instance.title, instance.owner.username),
    recipients = ['ywang@cigionline.org']  # hardcoded placeholder test recipients
    send_mail(
        'New Page Published',
        body,
        # os.environ['WAGTAILADMIN_NOTIFICATION_FROM_EMAIL'],
        'ywang@cigionline.org',
        recipients,
        fail_silently=False,
    )


def send_to_slack(instance):
    values = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "_%s_ \n By Author(s): name, name \n Published By: %s " % (instance.title, instance.owner.username),
                }
            }
        ]
    }
    url = os.environ['SLACK_WEBHOOK_URL']  # hardcoded placeholder test channel
    requests.post(url, json.dumps(values))


# Let everyone know when a new page is published
def send_notifications(sender, **kwargs):
    instance = kwargs['instance']
    send_to_slack(instance)
    send_email(instance)


class SignalsConfig(AppConfig):
    name = 'signals'
    verbose_name = "Signals"

    def ready(self):
        # importing model classes
        from articles.models import ArticlePage, ArticleSeriesPage
        from publications.models import PublicationPage
        from multimedia.models import MultimediaPage

        # Register a receiver
        page_published.connect(send_notifications, sender=ArticlePage)
        page_published.connect(send_notifications, sender=ArticleSeriesPage)
        page_published.connect(send_notifications, sender=PublicationPage)
        page_published.connect(send_notifications, sender=MultimediaPage)
