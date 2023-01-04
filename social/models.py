from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.fields import RichTextField
import os
import tweepy


@register_snippet
class Tweet(models.Model):
    title = models.CharField(max_length=255)
    tweet_id = models.CharField(max_length=255, unique=True)
    tweet_text = models.CharField(max_length=500, blank=True, null=True)
    tweet_url = models.CharField(max_length=255, blank=True, null=True)
    tweet_created_at = models.DateTimeField(blank=True, null=True)
    tweet_user_id = models.CharField(max_length=255, blank=True, null=True)
    tweet_user_name = models.CharField(max_length=255, blank=True, null=True)
    tweet_user_profile_image_url = models.CharField(max_length=255, blank=True, null=True)
    tweet_user_profile_image_url_https = models.CharField(max_length=255, blank=True, null=True)
    tweet_user_url = models.CharField(max_length=255, blank=True, null=True)
    tweet_user_username = models.CharField(max_length=255, blank=True, null=True)
    tweet_likes = models.IntegerField(blank=True, null=True)
    tweet_replies = models.IntegerField(blank=True, null=True)
    tweet_media_url = models.CharField(max_length=255, blank=True, null=True)
    tweet_media_key = models.CharField(max_length=255, blank=True, null=True)
    tweet_media_alt_text = models.CharField(max_length=255, blank=True, null=True)
    tweet_media_preview_image_url = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title

    panels = [
        FieldPanel('title'),
        FieldPanel('tweet_id'),
        FieldPanel('tweet_text'),
        FieldPanel('tweet_url'),
        FieldPanel('tweet_created_at'),
        FieldPanel('tweet_user_id'),
        FieldPanel('tweet_user_name'),
        FieldPanel('tweet_user_profile_image_url'),
        FieldPanel('tweet_user_url'),
        FieldPanel('tweet_user_username'),
        FieldPanel('tweet_likes'),
        FieldPanel('tweet_replies'),
        FieldPanel('tweet_media_url'),
        FieldPanel('tweet_media_key'),
        FieldPanel('tweet_media_alt_text'),
        FieldPanel('tweet_media_preview_image_url'),
    ]

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        bearer_token = os.environ.get('TWITTER_BEARER_TOKEN')
        expansions = ['author_id', 'attachments.media_keys']
        tweet_fields = ['author_id', 'created_at', 'public_metrics', 'text', 'attachments']
        media_fields = ['alt_text', 'media_key', 'preview_image_url', 'url']
        user_fields = ['name', 'url', 'profile_image_url', 'username']

        client = tweepy.Client(bearer_token)
        response = client.get_tweet(self.tweet_id, expansions=expansions, tweet_fields=tweet_fields, media_fields=media_fields, user_fields=user_fields)
        tweet = response.data

        try:
            public_metrics = tweet['public_metrics']
            user = response.includes['users'][0]
            media = response.includes['media'][0]
        except Exception:
            public_metrics = None
            user = None
            media = None

        self.tweet_text = tweet['text']
        self.tweet_created_at = tweet['created_at']

        if user:
            self.tweet_user_id = user['id']
            self.tweet_user_name = user['name']
            self.tweet_user_profile_image_url = user['profile_image_url']
            self.tweet_user_url = user['url']
            self.tweet_user_username = user['username']
            self.tweet_url = f'https://twitter.com/{user["username"]}/status/{self.tweet_id}'

        if public_metrics:
            self.tweet_likes = public_metrics['like_count'] if public_metrics['like_count'] else 0
            self.tweet_replies = public_metrics['reply_count'] if public_metrics['reply_count'] else 0

        if media:
            self.tweet_media_url = media['url']
            self.tweet_media_key = media['media_key']
            self.tweet_media_alt_text = media['alt_text']
            self.tweet_media_preview_image_url = media['preview_image_url']

        return super().save(force_insert, force_update, using, update_fields)


@register_snippet
class LinkedInPost(models.Model):
    title = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255, blank=True, null=True)
    user_username = models.CharField(max_length=255, blank=True, null=True)
    user_profile_image_url = models.CharField(max_length=255, blank=True, null=True)
    post_url = models.CharField(max_length=255, blank=True, null=True)
    post_text = RichTextField(blank=True, null=True)
    post_media_url = models.CharField(max_length=255, blank=True, null=True)
    post_created_at = models.DateTimeField(blank=True, null=True)
    post_likes = models.IntegerField(blank=True, null=True)
    post_comments = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title
