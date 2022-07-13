from django.db import models
from modelcluster.fields import ParentalKey
from streams.blocks import (
    ContactEmailBlock,
    ContactPersonBlock,
)
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.admin.mail import send_mail
from wagtail.fields import RichTextField, StreamField
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
        use_json_field=True,
    )
    human_resources_contact = StreamField(
        [
            ('contact_email', ContactEmailBlock()),
            ('contact_person', ContactPersonBlock(
                page_type='people.PersonPage',
            )),
        ],
        blank=True,
        use_json_field=True,
    )
    media_contact = StreamField(
        [
            ('contact_email', ContactEmailBlock()),
            ('contact_person', ContactPersonBlock(
                page_type='people.PersonPage',
            )),
        ],
        blank=True,
        use_json_field=True,
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
                FieldPanel('human_resources_contact'),
            ],
            heading='Human Resources',
        ),
        MultiFieldPanel(
            [
                FieldPanel('events_contact'),
            ],
            heading='Events',
        ),
        MultiFieldPanel(
            [
                FieldPanel('media_contact'),
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

    def send_mail(self, form):
        subject = f"[Contact Us] {form.data['subject']}"
        addresses = [x.strip() for x in self.to_address.split(',')]

        send_mail(subject, self.render_email(form), addresses, self.from_address,)

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = []
    template = 'contact/contact_page.html'
    landing_page_template = 'contact/contact_page_landing.html'

    class Meta:
        verbose_name = 'Contact Page'
