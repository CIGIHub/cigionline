import requests
import json
import os
import datetime
import pytz
import traceback
from distutils.log import error
from django.apps import AppConfig
from django.core.mail import EmailMultiAlternatives
from wagtail.contrib.frontend_cache.utils import purge_url_from_cache
from wagtail.signals import page_published


def get_env():
    # PYTHON_ENV values: 'production', 'admin', 'staging'
    if 'PYTHON_ENV' in os.environ:
        return os.environ.get('PYTHON_ENV')
    return 'dev'


def get_site_url():
    env = get_env()

    # values are the host root url intended for users' viewing. admin/production both return live site; staging returns staging site; dev returns local
    site_url_dict = {
        'admin': 'https://www.cigionline.org',
        'production': 'https://www.cigionline.org',
        'staging': 'https://staging.cigionline.org',
        'dev': 'http://localhost:8000'
    }
    return site_url_dict[env]


def datetime_compare(t1, t2):
    if t1:  # if go_live_at field is populated; if not, default False
        return ((t2.astimezone(pytz.utc) - t1.astimezone(pytz.utc)) <= datetime.timedelta(hours=1))
    return False


def count_publishes(instance):
    from wagtail.models import PageLogEntry

    latest_unpublish = PageLogEntry.objects.filter(page_id=instance.id, action='wagtail.unpublish').order_by('-timestamp')[0].timestamp
    all_publishes = PageLogEntry.objects.filter(page_id=instance.id, action='wagtail.publish', timestamp__gt=latest_unpublish)

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
    relative_url = instance.get_url_parts()[-1]  # last item in the tuple is the relative url to root; e.g. /articles/an-article/
    return title, authors, page_owner, content_type, publisher, is_first_publish, is_scheduled_publish, relative_url


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


def get_header_label():
    site_url = get_site_url()

    if site_url == 'http://localhost:8000':
        return 'dev environment'
    return site_url.replace('https://', '')


def send_email(title, authors, page_owner, content_type, recipients, publisher, publish_phrasing, page_url, header_label):
    text_content = f"{title} By Author(s): {authors} Page Created By: {page_owner} {publish_phrasing} By: {page_owner}"
    html_content = f"""
        <p><a href="{page_url}"><i>{title}</i></a></p>
        <p>By Author(s): {authors}</p>
        <p>Page Created By: {page_owner}</p>
        <p>{publish_phrasing} By: {publisher}</p>
        <p><i>You are receiving this update because you are on the publish notification list for: {content_type}<i></p>
    """
    email_title = f'[{header_label}] {title}'

    msg = EmailMultiAlternatives(
        email_title,  # title
        text_content,  # body
        os.environ['PUBLISHING_NOTIFICATION_FROM_EMAIL'],  # from email
        recipients,  # to emails
    )
    msg.attach_alternative(html_content, "text/html")

    if notifications_on():
        msg.send()
    # print email content when notification is off
    else:
        print(html_content)
    print('notification emails are sent to', recipients)


def send_to_slack(title, authors, page_owner, content_type, publisher, publish_phrasing, page_url, header_label):
    values = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"[{header_label}] <{page_url}|_{title}_> \n Type: {content_type} \n By Author(s): {authors} \n Page Created By: {page_owner} \n {publish_phrasing} By: {publisher}",
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

    title, authors, page_owner, content_type, publisher, is_first_publish, is_scheduled_publish, relative_url = instance_info(instance)
    publish_phrasing = set_publish_phrasing(is_first_publish)
    page_url = f'{get_site_url()}{relative_url}'
    header_label = get_header_label()

    # wrap in try/except to not disrupt normal operations if a page is successfully published but email could not be sent
    try:
        if is_first_publish:
            send_to_slack(title, authors, page_owner, content_type, publisher, publish_phrasing, page_url, header_label)
        notification_list = notification_email_list(notification_user_list(content_type, is_first_publish, is_scheduled_publish))
        send_email(title, authors, page_owner, content_type, notification_list, publisher, publish_phrasing, page_url, header_label)
    except Exception as e:
        print(e)


def clear_cloudflare_home_page_cache(sender, **kwargs):
    try:
        purge_url_from_cache('https://www.cigionline.org/')
    except Exception:
        error(traceback.format_exc())


class SignalsConfig(AppConfig):
    name = 'signals'
    verbose_name = "Signals"

    def ready(self):
        from articles.models import ArticlePage, ArticleSeriesPage
        from publications.models import PublicationPage
        from multimedia.models import MultimediaPage
        from events.models import EventPage
        from features.models import (
            HomePageFeaturedContentList,
            HomePageFeaturedPublicationsList,
            HomePageFeaturedMultimediaList,
            HomePageFeaturedEventsList,
            HomePageFeaturedHighlightsList,
            HomePageFeaturedPromotionsList,
            HomePageFeaturedExpertsList,
        )

        page_published.connect(send_notifications, sender=ArticlePage)
        page_published.connect(send_notifications, sender=ArticleSeriesPage)
        page_published.connect(send_notifications, sender=PublicationPage)
        page_published.connect(send_notifications, sender=MultimediaPage)
        page_published.connect(send_notifications, sender=EventPage)

        if 'CLOUDFLARE_EMAIL' in os.environ \
                and 'CLOUDFLARE_API_KEY' in os.environ \
                and 'CLOUDFLARE_ZONEID' in os.environ:
            page_published.connect(clear_cloudflare_home_page_cache, sender=HomePageFeaturedContentList)
            page_published.connect(clear_cloudflare_home_page_cache, sender=HomePageFeaturedPublicationsList)
            page_published.connect(clear_cloudflare_home_page_cache, sender=HomePageFeaturedMultimediaList)
            page_published.connect(clear_cloudflare_home_page_cache, sender=HomePageFeaturedEventsList)
            page_published.connect(clear_cloudflare_home_page_cache, sender=HomePageFeaturedHighlightsList)
            page_published.connect(clear_cloudflare_home_page_cache, sender=HomePageFeaturedPromotionsList)
            page_published.connect(clear_cloudflare_home_page_cache, sender=HomePageFeaturedExpertsList)
