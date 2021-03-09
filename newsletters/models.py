from core.models import (
    BasicPageAbstract,
)
from django.db import models
from django.template.loader import render_to_string
from streams.blocks import (AdvertisementBlock, ContentBlock, FeaturedContentBlock, SocialBlock, TextBlock)
from wagtail.admin.edit_handlers import MultiFieldPanel, StreamFieldPanel
from wagtail.core.blocks import (
    BooleanBlock,
    CharBlock,
    ChoiceBlock,
    PageChooserBlock,
    RichTextBlock,
    StructBlock,
    URLBlock,
)
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.blocks import ImageChooserBlock


class NewsletterListPage(BasicPageAbstract, Page):
    max_count = 1
    parent_page_types = ['home.Homepage']
    subpage_types = ['newsletters.NewsletterPage']
    templates = 'newsletters/newsletter_list_page.html'

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    class Meta:
        verbose_name = 'Newsletter List Page'


class NewsletterPage(Page):
    class CallToActionChoices(models.TextChoices):
        EXPLORE = ('explore', 'Explore')
        FOLLOW = ('follow', 'Follow')
        LEARN_MORE = ('learn_more', 'Learn More')
        LISTEN = ('listen', 'Listen')
        NO_CTA = ('no_cta', 'No CTA')
        PDF = ('pdf', 'PDF')
        READ = ('read', 'Read')
        RSVP = ('rsvp', 'RSVP')
        SHARE_FACEBOOK = ('share_facebook', 'Share (Facebook)')
        SHARE_LINKEDIN = ('share_linkedin', 'Share (LinkedIn)')
        SHARE_TWITTER = ('share_twitter', 'Share (Twitter)')
        SUBSCRIBE = ('subscribe', 'Subscribe')
        WATCH = ('watch', 'Watch')

    body = StreamField(
        [
            ('advertisement_block', AdvertisementBlock()),
            ('content_block', ContentBlock()),
            ('featured_content_block', FeaturedContentBlock()),
            ('social_block', SocialBlock()),
            ('text_block', TextBlock()),
        ],
        blank=True,
    )
    html_file = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                StreamFieldPanel('body'),
            ],
            heading='Body',
            classname='collapsible',
        ),
        MultiFieldPanel(
            [
                DocumentChooserPanel('html_file'),
            ],
            heading='HTML File',
            classname='collapsible collapsed',
        ),
    ]

    def html_string(self):
        return render_to_string('newsletters/newsletter_html.html', {'self': self, 'page': self})

    parent_page_types = ['newsletters.NewsletterListPage']
    subpage_types = []
    templates = 'newsletters/newsletter_page.html'

    class Meta:
        verbose_name = 'Newsletter'
        verbose_name_plural = 'Newsletters'
