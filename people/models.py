from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Page


class PersonListPage(Page):
    """Person list page"""

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = ['people.PersonPage']
    templates = 'people/person_list_page.html'

    class Meta:
        verbose_name = 'Person List Page'


class PersonPage(Page):
    """View person page"""
    address_city = models.CharField(blank=True, max_length=255)
    address_country = models.CharField(blank=True, max_length=255)
    address_line1 = models.CharField(blank=True, max_length=255)
    address_line2 = models.CharField(blank=True, max_length=255)
    address_postal_code = models.CharField(blank=True, max_length=32)
    address_province = models.CharField(blank=True, max_length=255)
    body = StreamField([
        ('paragraph', blocks.RichTextBlock())
    ], blank=True)
    email = models.EmailField(blank=True)
    first_name = models.CharField(blank=True, max_length=255)
    last_name = models.CharField(blank=True, max_length=255)
    phone_number = models.CharField(blank=True, max_length=32)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('first_name'),
            FieldPanel('last_name'),
            FieldPanel('email'),
            FieldPanel('phone_number')
        ], heading='General Information'),
        MultiFieldPanel([
            StreamFieldPanel('body')
        ], heading='Biography'),
        MultiFieldPanel([
            FieldPanel('address_line1'),
            FieldPanel('address_line2'),
            FieldPanel('address_city'),
            FieldPanel('address_province'),
            FieldPanel('address_postal_code'),
            FieldPanel('address_country')
        ], heading='Address')
    ]
    parent_page_types = ['people.PersonListPage']
    subpage_types = []
    templates = 'people/person_page.html'

    class Meta:
        verbose_name = 'Person Page'
        verbose_name_plural = 'Person Pages'
