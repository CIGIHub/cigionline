from unittest.mock import Mock

from wagtail.test.utils import WagtailPageTestCase
from subscribe.models import SubscribePage
from home.models import HomePage


class SubscribePageTests(WagtailPageTestCase):
    def test_subscribepage_parent_page_types(self):
        self.assertAllowedParentPageTypes(
            SubscribePage,
            {HomePage},
        )

    def test_subscribepage_child_page_types(self):
        self.assertAllowedSubpageTypes(
            SubscribePage,
            {},
        )

    def test_apply_tag_includes_anniversary_tag(self):
        client = Mock()

        SubscribePage().apply_tag(
            client,
            'list-id',
            'subscriber-hash',
            extra_tags=['25 Anniversary'],
        )

        client.lists.update_list_member_tags.assert_called_once_with(
            'list-id',
            'subscriber-hash',
            {
                'tags': [
                    {'name': 'CIGI Weekly Newsletter', 'status': 'active'},
                    {'name': '25 Anniversary', 'status': 'active'},
                ],
            },
        )
