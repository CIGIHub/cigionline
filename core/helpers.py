from wagtail_modeladmin.helpers import PagePermissionHelper


class CIGIModelAdminPermissionHelper(PagePermissionHelper):
    def user_can_list(self, user):
        return self.user_has_any_permissions(user)
