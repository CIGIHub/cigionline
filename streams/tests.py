from django.test import SimpleTestCase
from wagtail import blocks

from streams.blocks import ButtonBlock


class ButtonBlockTests(SimpleTestCase):
    def test_requires_page_or_url(self):
        with self.assertRaises(blocks.StructBlockValidationError):
            ButtonBlock().clean({
                'text': 'Read more',
                'page': None,
                'url': '',
            })
