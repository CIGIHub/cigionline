from wagtail import hooks
from wagtail.admin.ui.tables import Column
from utils.admin_utils import title_with_actions
from wagtail.admin.viewsets.model import ModelViewSet

from .models import PromotionBlock


class PromotionBlockViewSet(ModelViewSet):
    model = PromotionBlock
    menu_label = 'Promotion Blocks'
    menu_icon = 'image'
    menu_order = 203
    icon = 'image'
    list_display = [
        Column(title_with_actions, label='Title', sort_key='name'),
        Column('block_type', label='Block Type', sort_key='block_type'),
    ]
    exclude_form_fields = []
    search_fields = ('name',)
    ordering = ['name']
    add_to_admin_menu = True


@hooks.register('register_admin_viewset')
def register_promotion_block_viewset():
    return PromotionBlockViewSet()
