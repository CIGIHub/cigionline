from wagtail.contrib.modeladmin.helpers import PermissionHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import Menu


# Menus are not allowed to be created in the admin interface. To add/remove a
# menu, a migration needs to be created.
class MenuAdminPermissionHelper(PermissionHelper):
    def user_can_list(self, user):
        return True

    def user_can_create(self, user):
        return True

    def user_can_edit_obj(self, user, obj):
        return True

    def user_can_delete_obj(self, user, obj):
        return True


class MenuAdmin(ModelAdmin):
    model = Menu
    menu_label = 'Menus'
    menu_icon = 'list-ul'
    menu_order = 100
    ordering = ['name']
    permission_helper_class = MenuAdminPermissionHelper
    add_to_settings_menu = True
    exclude_from_explorer = False


modeladmin_register(MenuAdmin)
