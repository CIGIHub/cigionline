from wagtail import hooks
from wagtail.admin.ui.tables import Column
from utils.admin_utils import title_with_actions
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import PromotionBlock


class PromotionBlockViewSet(SnippetViewSet):
    model = PromotionBlock
    menu_label = 'Promotion Blocks'
    menu_icon = 'image'
    menu_order = 203
    list_display = [
        Column(title_with_actions, label='Title', sort_key='name'),
        Column('block_type', label='Block Type', sort_key='block_type'),
    ]
    form_fields = ['name', 'block_type']
    search_fields = ('name',)
    ordering = ['name']
    add_to_admin_menu = True


@hooks.register('register_admin_viewset')
def register_promotion_block_viewset():
    return PromotionBlockViewSet()
