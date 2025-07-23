from .models import Menu
from wagtail import hooks
from wagtail.admin.ui.tables import Column
from utils.admin_utils import title_with_actions
from wagtail.admin.viewsets.model import ModelViewSet

# Menus are not allowed to be created in the admin interface. To add/remove a
# menu, a migration needs to be created.


class MenuViewSet(ModelViewSet):
    model = Menu
    menu_label = 'Menus'
    menu_icon = 'list-ul'
    menu_order = 100
    icon = 'list-ul'
    list_display = [
        Column(title_with_actions, label='Title', sort_key='name'),
    ]
    exclude_form_fields = []
    search_fields = ('name',)
    ordering = ['name']
    add_to_settings_menu = True


@hooks.register('register_admin_viewset')
def register_menu_viewset():
    return MenuViewSet()
