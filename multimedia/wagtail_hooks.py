from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from wagtail.contrib.modeladmin.helpers import PagePermissionHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks

from .models import MultimediaPage


@hooks.register('register_permissions')
def register_multimedia_page_permissions():
    multimedia_content_type = ContentType.objects.get(app_label='multimedia', model='multimediapage')
    return Permission.objects.filter(content_type=multimedia_content_type)


class MultimediaPageModelAdminPermissionHelper(PagePermissionHelper):
    def user_can_list(self, user):
        return self.user_has_any_permissions(user)


class MultimediaPageModelAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = MultimediaPage
    menu_label = 'Multimedia'
    menu_icon = 'media'
    menu_order = 102
    list_display = ('title', 'publishing_date', 'multimedia_type', 'multimedia_series', 'theme', 'live')
    list_filter = ('publishing_date', 'multimedia_type', 'multimedia_series', 'theme', 'live')
    search_fields = ('title', 'multimedia_type', 'multimedia_series',)
    ordering = ['-publishing_date']
    permission_helper_class = MultimediaPageModelAdminPermissionHelper

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(publishing_date__isnull=False)


modeladmin_register(MultimediaPageModelAdmin)
