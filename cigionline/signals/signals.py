from wagtail.core.signals import page_published
from articles.models import ArticlePage
import requests
import json
import os


# Let everyone know when a new page is published
def send_to_slack(sender, **kwargs):
    instance = kwargs['instance']
    url = os.environ['SLACK_WEBHOOK_URL']
    values = {
        "text": "%s was published by %s " % (instance.title, instance.owner.username),
    }

    requests.post(url, json.dumps(values))


# Register a receiver
page_published.connect(send_to_slack, sender=ArticlePage)
