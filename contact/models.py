from django.db import models
from modelcluster.fields import ParentalKey
from streams.blocks import (
    ContactEmailBlock,
    ContactPersonBlock,
)
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    StreamFieldPanel,
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.contrib.forms.models import (
    AbstractEmailForm,
    AbstractFormField,
)


class ContactFormField(AbstractFormField):
    page = ParentalKey(
        'contact.ContactPage',
        on_delete=models.CASCADE,
        related_name='form_fields',
    )


class ContactPage(AbstractEmailForm):
    events_contact = StreamField(
        [
            ('contact_email', ContactEmailBlock()),
            ('contact_person', ContactPersonBlock(
                page_type='people.PersonPage',
            )),
        ],
        blank=True,
    )
    human_resources_contact = StreamField(
        [
            ('contact_email', ContactEmailBlock()),
            ('contact_person', ContactPersonBlock(
                page_type='people.PersonPage',
            )),
        ],
        blank=True,
    )
    media_contact = StreamField(
        [
            ('contact_email', ContactEmailBlock()),
            ('contact_person', ContactPersonBlock(
                page_type='people.PersonPage',
            )),
        ],
        blank=True,
    )
    thank_you_message = RichTextField(
        blank=True,
        null=False,
        features=['bold', 'italic', 'link'],
    )

    content_panels = AbstractEmailForm.content_panels + [
        InlinePanel('form_fields', label='Form Fields'),
        FieldPanel('thank_you_message'),
        MultiFieldPanel(
            [
                FieldPanel('from_address'),
                FieldPanel('to_address'),
                FieldPanel('subject'),
            ],
            heading='Email Settings',
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('human_resources_contact'),
            ],
            heading='Human Resources',
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('events_contact'),
            ],
            heading='Events',
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('media_contact'),
            ],
            heading='Media',
        ),
    ]

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for name, field in form.fields.items():
            placeholder = field.help_text
            if field.required:
                placeholder = placeholder + '*'
            field.widget.attrs.update({'placeholder': placeholder})
        return form

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = []
    template = 'contact/contact_page.html'
    landing_page_template = 'contact/contact_page_landing.html'

    class Meta:
        verbose_name = 'Contact Page'
