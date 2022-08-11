import requests
import json
import os
from wagtail.core.signals import page_published
from django.apps import AppConfig


# Let everyone know when a new page is published
def send_to_slack(sender, **kwargs):
    instance = kwargs['instance']
    url = os.environ['SLACK_WEBHOOK_URL']
    values = {
        "text": "%s was published by %s " % (instance.title, instance.owner.username),
    }

    requests.post(url, json.dumps(values))


class SignalsConfig(AppConfig):
    name = 'signals'
    verbose_name = "Signals"

    def ready(self):
        # importing model classes
        from articles.models import ArticlePage, ArticleSeriesPage
        from publications.models import PublicationPage
        from multimedia.models import MultimediaPage

        # Register a receiver
        page_published.connect(send_to_slack, sender=ArticlePage)
        page_published.connect(send_to_slack, sender=ArticleSeriesPage)
        page_published.connect(send_to_slack, sender=PublicationPage)
        page_published.connect(send_to_slack, sender=MultimediaPage)
