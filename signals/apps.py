import requests
import json
import os
from wagtail.core.signals import page_published
from django.apps import AppConfig
from django.core.mail import EmailMultiAlternatives


# def user_info(user_id):
#     from django.contrib.auth.models import User

#     return User.objects.get(id=user_id)


def instance_info(instance):
    title = instance.title
    authors = ', '.join(instance.author_names)
    page_owner = f'{instance.owner.first_name} {instance.owner.last_name}'
    content_type = 'Articles' if instance.contenttype == 'Opinion' else instance.contenttype  # adjust ContentPage.contenttype to match page_type
    publisher = f'{instance.get_latest_revision().user.first_name} {instance.get_latest_revision().user.last_name}'
    print(publisher)
    # print('go live: ', instance.go_live_at)
    # print('last published: ', instance.last_published_at)
    # print('first published: ', instance.first_published_at)
    # print('revision id: ', instance.live_revision_id)
    return title, authors, page_owner, content_type


def notification_user_list(content_type):
    print(f'compiling user list for content type: {content_type}')
    from .models import PublishEmailNotification

    return PublishEmailNotification.objects.filter(page_type_permissions__page_type__title__contains=content_type)


def notification_email_list(notification_user_list):
    print(f'compiling email list for users: {notification_user_list}')
    from django.contrib.auth.models import User

    return [User.objects.get(id=user_to_notify.user.user_id).email for user_to_notify in notification_user_list]


def send_email(title, authors, page_owner, content_type, recipients):
    text_content = f"{title} By Author(s): {authors} Published By: {page_owner}"
    html_content = f"""
        <p><i>{title}</i></p>
        <p>By Author(s): {authors}</p>
        <p>Published By: {page_owner}</p>
        <p><i>You are receiving this update because you are on the publish notification list for: {content_type}<i></p>
    """

    msg = EmailMultiAlternatives(
        "New Page Published",  # title
        text_content,  # body
        os.environ['PUBLISHING_NOTIFICATION_FROM_EMAIL'],  # from email
        recipients,  # to emails
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()
    print('notification emails are sent to', recipients)


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

    if 'NOTIFICATIONS_ON' in os.environ and (os.environ['NOTIFICATIONS_ON'].lower() == "true"):
        requests.post(url, json.dumps(values))


# Let everyone know when a new page is published
def send_notifications(sender, **kwargs):
    instance = kwargs['instance']

    title, authors, page_owner, content_type = instance_info(instance)

    # wrap in try/except to not disrupt normal operations if a page is successfully published but email could not be sent
    try:
        notification_list = notification_email_list(notification_user_list(content_type))
        send_to_slack(title, authors, page_owner)
        send_email(title, authors, page_owner, content_type, notification_list)
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
