import requests
import json
import os
import datetime
import pytz
from wagtail.core.signals import page_published
from django.apps import AppConfig
from django.core.mail import EmailMultiAlternatives


def datetime_compare(t1, t2):
    if t1:  # if go_live_at field is populated; if not, default False
        return ((t2.astimezone(pytz.utc) - t1.astimezone(pytz.utc)) <= datetime.timedelta(hours=1))
    return False


def count_publishes(instance):
    from wagtail.core.models import PageLogEntry

    all_publishes = PageLogEntry.objects.filter(page_id=instance.id, action='wagtail.publish')

    # for some reason, the PageLogEntry objects are not including the most recent publish that triggered this script
    # so a first-time publish would have a count of 0
    is_first_publish = (len(all_publishes) == 0)

    if instance.go_live_at:
        publishes_since_go_live_at = PageLogEntry.objects.filter(page_id=instance.id, action='wagtail.publish', timestamp__gte=instance.go_live_at)
        is_first_publish_since_go_live_at = (len(publishes_since_go_live_at) == 0)
    else:
        is_first_publish_since_go_live_at = False
    return is_first_publish, is_first_publish_since_go_live_at


def instance_info(instance):
    title = instance.title
    authors = ', '.join(instance.author_names)
    page_owner = f'{instance.owner.first_name} {instance.owner.last_name}'
    content_type = 'Articles' if instance.contenttype == 'Opinion' else instance.contenttype  # adjust ContentPage.contenttype to match page_type
    publisher = f'{instance.get_latest_revision().user.first_name} {instance.get_latest_revision().user.last_name}'
    is_first_publish, is_first_publish_since_go_live_at = count_publishes(instance)
    is_scheduled_publish = (datetime_compare(instance.go_live_at, instance.last_published_at) and is_first_publish_since_go_live_at)
    print(f'first: {is_first_publish}, scheduled: {is_scheduled_publish}')
    return title, authors, page_owner, content_type, publisher, is_first_publish, is_scheduled_publish


def notification_user_list(content_type, is_first_publish, is_scheduled_publish):
    print(f'compiling user list for content type: {content_type}')
    from .models import PublishEmailNotification

    user_list = PublishEmailNotification.objects.filter(page_type_permissions__page_type__title__contains=content_type)

    # additional filter based on scanerios created by combinations of the two flags
    if is_first_publish:
        user_list = user_list.filter(state_opt_in__in=('first_time', 'both'))
    else:
        user_list = user_list.filter(state_opt_in__in=('republish', 'both'))
    if is_scheduled_publish:
        user_list = user_list.filter(trigger_opt_in__in=('scheduled', 'both'))
    else:
        user_list = user_list.filter(trigger_opt_in__in=('manual', 'both'))
    return user_list


def notification_email_list(notification_user_list):
    print(f'compiling email list for users: {notification_user_list}')

    # going through User model because PublishEmailNotification returns UserProfile objects which has no 'email' attribute
    from django.contrib.auth.models import User

    return [User.objects.get(id=user_to_notify.user.user_id).email for user_to_notify in notification_user_list]


def notifications_on():
    return ('NOTIFICATIONS_ON' in os.environ and (os.environ['NOTIFICATIONS_ON'].lower() == "true"))


def set_publish_phrasing(is_first_publish):
    if is_first_publish:
        return 'Published'
    return 'Republished'


def send_email(title, authors, page_owner, content_type, recipients, publisher, publish_phrasing):
    text_content = f"{title} By Author(s): {authors} Page Created By: {page_owner} {publish_phrasing} By: {page_owner}"
    html_content = f"""
        <p><i>{title}</i></p>
        <p>By Author(s): {authors}</p>
        <p>Page Created By: {page_owner}</p>
        <p>{publish_phrasing} By: {publisher}</p>
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
    # print email content when notification is off
    if not notifications_on():
        print(html_content)


def send_to_slack(title, authors, page_owner, publisher, publish_phrasing):
    values = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"_{title}_ \n By Author(s): {authors} \n Page Created By: {page_owner} \n {publish_phrasing} By: {publisher}",
                }
            }
        ]
    }
    url = os.environ['SLACK_WEBHOOK_URL']  # hardcoded placeholder test channel

    if notifications_on():
        requests.post(url, json.dumps(values))
    else:
        print(values)  # print what would've been sent to Slack


# Let everyone know when a new page is published
def send_notifications(sender, **kwargs):
    instance = kwargs['instance']

    title, authors, page_owner, content_type, publisher, is_first_publish, is_scheduled_publish = instance_info(instance)
    publish_phrasing = set_publish_phrasing(is_first_publish)

    # wrap in try/except to not disrupt normal operations if a page is successfully published but email could not be sent
    try:
        if is_first_publish:
            send_to_slack(title, authors, page_owner, publisher, publish_phrasing)
        notification_list = notification_email_list(notification_user_list(content_type, is_first_publish, is_scheduled_publish))
        send_email(title, authors, page_owner, content_type, notification_list, publisher, publish_phrasing)
    except Exception as e:
        print(e)


class SignalsConfig(AppConfig):
    name = 'signals'
    verbose_name = "Signals"

    def ready(self):
        from articles.models import ArticlePage, ArticleSeriesPage
        from publications.models import PublicationPage
        from multimedia.models import MultimediaPage
        from events.models import EventPage

        page_published.connect(send_notifications, sender=ArticlePage)
        page_published.connect(send_notifications, sender=ArticleSeriesPage)
        page_published.connect(send_notifications, sender=PublicationPage)
        page_published.connect(send_notifications, sender=MultimediaPage)
        page_published.connect(send_notifications, sender=EventPage)
