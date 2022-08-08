from wagtail.core.signals import page_published
import requests
import json


# Let everyone know when a new page is published
def send_to_slack(sender, **kwargs):
    instance = kwargs['instance']
    url = 'https://hooks.slack.com/services/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'
    values = {
        "text": "%s was published by %s " % (instance.title, instance.owner.username),
    }

    response = requests.post(url, json.dumps(values))
    print(response.text)


# Register a receiver
page_published.connect(send_to_slack)
