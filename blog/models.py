from django.db import models
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.edit_handlers import (
    FieldPanel
)
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page


class ContentPage(Page):
    publishing_date = models.DateTimeField(blank=False, null=True)
    topics = ParentalManyToManyField('research.TopicPage', blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('publishing_date'),
        FieldPanel('topics'),
    ]

    def on_form_bound(self):
        self.bound_field = self.form[self.field_name]
        heading = self.heading or self.bound_field.label
        self.heading = heading
        self.bound_field.label = heading


class BlogArticlePage(ContentPage):
    subtitle = RichTextField(blank=True, null=False)

    content_panels = ContentPage.content_panels + [
        FieldPanel('subtitle'),
    ]


class BlogEventPage(ContentPage):
    content_panels = Page.content_panels + [
        FieldPanel('publishing_date', heading='Event start'),
        FieldPanel('topics'),
    ]


class BlogVideoPage(ContentPage):
    youtube_id = models.CharField(max_length=32)

    content_panels = ContentPage.content_panels + [
        FieldPanel('youtube_id'),
    ]
