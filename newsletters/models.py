from core.models import (
    BasicPageAbstract,
    SearchablePageAbstract,
)
from django.db import models
from django.template.loader import render_to_string
from streams.blocks import (
    AdvertisementBlock,
    ContentBlock,
    FeaturedContentBlock,
    SocialBlock,
    TextBlock,
    AdvertisementBlockLarge,
    FeaturedContentBlockLarge,
)
from wagtail.admin.panels import MultiFieldPanel, FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from bs4 import BeautifulSoup
from django.utils.text import slugify


class NewsletterListPage(BasicPageAbstract, SearchablePageAbstract, Page):
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

    search_fields = Page.search_fields + BasicPageAbstract.search_fields + SearchablePageAbstract.search_fields

    class Meta:
        verbose_name = 'Newsletter List Page'


class NewsletterPage(Page):
    body = StreamField(
        [
            ('advertisement_block', AdvertisementBlock(label='Advertisement Block (Old)', classname='hidden')),
            ('advertisement_block_large', AdvertisementBlockLarge()),
            ('content_block', ContentBlock()),
            ('featured_content_block', FeaturedContentBlock(label='Featured Content Block (Old)', classname='hidden')),
            ('featured_content_block_large', FeaturedContentBlockLarge()),
            ('social_block', SocialBlock()),
            ('text_block', TextBlock()),
        ],
        blank=True,
        use_json_field=True,
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
                FieldPanel('body'),
            ],
            heading='Body',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('html_file'),
            ],
            heading='HTML File',
            classname='collapsible collapsed',
        ),
    ]

    def html_string(self):
        def in_line_tracking(href, title):
            tracking = f'utm_source=cigi_newsletter&utm_medium=email&utm_campaign={slugify(title)}'
            if '?' in href:
                return f'{href}&{tracking}'
            else:
                return f'{href}?{tracking}'

        text_soup = BeautifulSoup(render_to_string('newsletters/newsletter_html.html',
                                                   {'self': self, 'page': self, 'is_html_string': True}),
                                  'html.parser')

        for link in text_soup.findAll('a'):
            try:
                link['href'] = in_line_tracking(link['href'], self.title)
            except KeyError:
                pass

        return str(text_soup)

    parent_page_types = ['newsletters.NewsletterListPage']
    subpage_types = []
    templates = 'newsletters/newsletter_page.html'

    class Meta:
        verbose_name = 'Newsletter'
        verbose_name_plural = 'Newsletters'
