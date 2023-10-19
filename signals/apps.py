import requests
import json
import os
import datetime
import pytz
import traceback
from django.core.cache import cache
from distutils.log import error
from django.apps import AppConfig
from django.core.mail import EmailMultiAlternatives
from wagtail.contrib.frontend_cache.utils import purge_url_from_cache
from wagtail.signals import page_published


class InstanceInfo():
    def __init__(self, instance):
        self.instance = instance
        self.title = instance.title
        self.authors = ', '.join(instance.author_names)
        self.page_owner = f'{instance.owner.first_name} {instance.owner.last_name}'
        self.content_type = 'Articles' if instance.contenttype == 'Opinion' else instance.contenttype  # adjust ContentPage.contenttype to match page_type
        self.publisher = f'{instance.get_latest_revision().user.first_name} {instance.get_latest_revision().user.last_name}'
        self.relative_url = instance.get_url_parts()[-1]  # last item in the tuple is the relative url to root; e.g. /articles/an-article/


class NotificationFlags(InstanceInfo):
    def __init__(self, instance):
        super().__init__(instance)

    def _datetime_compare(self, t1, t2):
        """
        t1: go_live_at field
        t2: last_published_at field

        if go_live_at field is populated, compare last_published_at to go_live_at
        if not, default False
        """
        if t1:
            return ((t2.astimezone(pytz.utc) - t1.astimezone(pytz.utc)) <= datetime.timedelta(hours=1))
        return False

    def _count_publishes(self):
        from wagtail.models import PageLogEntry

        all_unpublishes = PageLogEntry.objects.filter(page_id=self.instance.id, action='wagtail.unpublish').order_by('-timestamp')
        if all_unpublishes:
            latest_unpublish = all_unpublishes[0].timestamp
            all_publishes = PageLogEntry.objects.filter(page_id=self.instance.id, action='wagtail.publish', timestamp__gt=latest_unpublish)
        else:
            all_publishes = PageLogEntry.objects.filter(page_id=self.instance.id, action='wagtail.publish')

        # for some reason, the PageLogEntry objects are not including the most recent publish that triggered this script
        # so a first-time publish would have a count of 0
        is_first_publish = (len(all_publishes) == 0)

        if self.instance.go_live_at:
            publishes_since_go_live_at = PageLogEntry.objects.filter(page_id=self.instance.id, action='wagtail.publish', timestamp__gte=self.instance.go_live_at)
            is_first_publish_since_go_live_at = (len(publishes_since_go_live_at) == 0)
        else:
            is_first_publish_since_go_live_at = False
        return is_first_publish, is_first_publish_since_go_live_at

    @property
    def is_first_publish(self):
        return self._count_publishes()[0]

    @property
    def is_first_publish_since_go_live_at(self):
        return self._count_publishes()[1]

    @property
    def is_scheduled_publish(self):
        return (self._datetime_compare(self.instance.go_live_at, self.instance.last_published_at) and self.is_first_publish_since_go_live_at)

    @property
    def is_notifications_on(self):
        return ('NOTIFICATIONS_ON' in os.environ and (os.environ['NOTIFICATIONS_ON'].lower() == "true"))


class NotificationRecipients(NotificationFlags):
    """
    Determine recipients based on flags
    """

    def __init__(self, instance):
        super().__init__(instance)

    def get_user_list(self):
        from .models import PublishEmailNotification

        user_list = PublishEmailNotification.objects.filter(page_type_permissions__page_type__title__contains=self.content_type)

        # additional filter based on scanerios created by combinations of the two flags
        if self.is_first_publish:
            user_list = user_list.filter(state_opt_in__in=('first_time', 'both'))
        else:
            user_list = user_list.filter(state_opt_in__in=('republish', 'both'))
        if self.is_scheduled_publish:
            user_list = user_list.filter(trigger_opt_in__in=('scheduled', 'both'))
        else:
            user_list = user_list.filter(trigger_opt_in__in=('manual', 'both'))
        return user_list

    @property
    def email_list(self):
        # going through User model because PublishEmailNotification returns UserProfile objects which has no 'email' attribute
        from django.contrib.auth.models import User

        return [User.objects.get(id=user_to_notify.user.user_id).email for user_to_notify in self.get_user_list()]


class NotificationContent(NotificationRecipients):

    def get_site_url(self):
        """
        PYTHON_ENV values: 'production', 'admin', 'staging'

        return values are the host root url intended for users' viewing
        admin/production both return live site
        staging returns staging site; dev returns local
        """
        env = os.environ.get('PYTHON_ENV') if 'PYTHON_ENV' in os.environ else 'dev'

        site_url_dict = {
            'admin': 'https://www.cigionline.org',
            'production': 'https://www.cigionline.org',
            'staging': 'https://staging.cigionline.org',
            'dev': 'http://localhost:8000'
        }
        return site_url_dict[env]

    @property
    def page_url(self):
        return f'{self.get_site_url()}{self.relative_url}'

    @property
    def publish_phrasing(self):
        if self.is_first_publish:
            return 'Published'
        return 'Republished'

    @property
    def header_label(self):
        site_url = self.get_site_url()
        if site_url == 'http://localhost:8000':
            return 'dev environment'
        return site_url.replace('https://', '')

    def send_email(self):
        text_content = f"{self.title} By Author(s): {self.authors} Page Created By: {self.page_owner} {self.publish_phrasing} By: {self.page_owner}"
        html_content = f"""
            <p><a href="{self.page_url}"><i>{self.title}</i></a></p>
            <p>By Author(s): {self.authors}</p>
            <p>Page Created By: {self.page_owner}</p>
            <p>{self.publish_phrasing} By: {self.publisher}</p>
            <p><i>You are receiving this update because you are on the publish notification list for: {self.content_type}<i></p>
        """
        email_title = f'[{self.header_label}] {self.title}'

        msg = EmailMultiAlternatives(
            email_title,  # title
            text_content,  # body
            os.environ['PUBLISHING_NOTIFICATION_FROM_EMAIL'],  # from email
            self.email_list,  # to emails
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def send_to_slack(self):
        values = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"[{self.header_label}] <{self.page_url}|_{self.title}_> \n Type: {self.content_type} \n By Author(s): {self.authors} \n Page Created By: {self.page_owner} \n {self.publish_phrasing} By: {self.publisher}",
                    }
                }
            ]
        }
        url = os.environ['SLACK_WEBHOOK_URL']
        requests.post(url, json.dumps(values))


def send_notifications(sender, **kwargs):
    instance = kwargs['instance']
    publish_notification = NotificationContent(instance)

    # wrap in try/except to not disrupt normal operations if a page is successfully published but email could not be sent
    if publish_notification.is_notifications_on:
        try:
            if publish_notification.is_first_publish:
                publish_notification.send_to_slack()
            publish_notification.send_email()
        except Exception as e:
            print(e)


def clear_cloudflare_home_page_cache(sender, **kwargs):
    try:
        purge_url_from_cache('https://www.cigionline.org/')
    except Exception:
        error(traceback.format_exc())


def clear_experts_page_cache(sender, **kwargs):
    # clear experts landing page search table cache if a new expert is added or a person gains or loses the 'expert' role, or if an expert's expertise field is updated
    from wagtail.models import Revision

    revision = kwargs['revision']

    try:
        revision_previous = revision.get_previous()
    except Revision.DoesNotExist:
        revision_previous = None

    try:
        if (not revision_previous and 4 in revision.content['person_types']) \
                or (revision.content['person_types'] != revision_previous.content['person_types']) \
                or (4 in revision.content['person_types'] and revision.content['expertise'] != revision_previous.content['expertise']):
            cache.delete_pattern('*all_experts*')
            purge_url_from_cache('https://www.cigionline.org/experts/')

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
        from people.models import PersonPage
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

        if 'PYTHON_ENV' in os.environ \
                and (os.environ.get('PYTHON_ENV') == 'production' or os.environ.get('PYTHON_ENV') == 'admin') \
                and 'CLOUDFLARE_EMAIL' in os.environ \
                and 'CLOUDFLARE_API_KEY' in os.environ \
                and 'CLOUDFLARE_ZONEID' in os.environ:
            page_published.connect(clear_cloudflare_home_page_cache, sender=HomePageFeaturedContentList)
            page_published.connect(clear_cloudflare_home_page_cache, sender=HomePageFeaturedPublicationsList)
            page_published.connect(clear_cloudflare_home_page_cache, sender=HomePageFeaturedMultimediaList)
            page_published.connect(clear_cloudflare_home_page_cache, sender=HomePageFeaturedEventsList)
            page_published.connect(clear_cloudflare_home_page_cache, sender=HomePageFeaturedHighlightsList)
            page_published.connect(clear_cloudflare_home_page_cache, sender=HomePageFeaturedPromotionsList)
            page_published.connect(clear_cloudflare_home_page_cache, sender=HomePageFeaturedExpertsList)
            page_published.connect(clear_experts_page_cache, sender=PersonPage)
