from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
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
    tweet_likes = models.IntegerField(blank=True, null=True)
    tweet_replies = models.IntegerField(blank=True, null=True)

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
        FieldPanel('tweet_likes'),
        FieldPanel('tweet_replies'),
    ]

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        expansions = ['author_id', 'attachments.media_keys']
        tweet_fields = ['author_id', 'created_at', 'public_metrics', 'text']
        media_fields = ['alt_text', 'media_key', 'preview_image_url', 'url']
        user_fields = ['name', 'url', 'profile_image_url']

        client = tweepy.Client('AAAAAAAAAAAAAAAAAAAAANq9kQEAAAAAiFirRFj9KPnG4kspZ17rZuT0bd0%3Drr0wAyQ40Kq3KiXBCH879YaWQfp1ZMbwSAO803ArXPUS1uD4XF')
        response = client.get_tweet(self.tweet_id, expansions=expansions, tweet_fields=tweet_fields, media_fields=media_fields, user_fields=user_fields)
        tweet = response.data

        public_metrics = tweet['public_metrics']
        user = response.includes['users'][0]

        self.tweet_text = tweet['text']
        self.tweet_created_at = tweet['created_at']
        self.tweet_user_id = user['id']
        self.tweet_user_name = user['name']
        self.tweet_user_profile_image_url = user['profile_image_url']
        self.tweet_user_url = user['url']
        self.tweet_likes = public_metrics['like_count']
        self.tweet_replies = public_metrics['reply_count']

        super().save(force_insert, force_update, using, update_fields)
