from core.helpers import CIGIModelAdminPermissionHelper
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks

from .models import PublicationPage


@hooks.register('register_permissions')
def register_publication_page_permissions():
    publication_content_type = ContentType.objects.get(app_label='publications', model='publicationpage')
    return Permission.objects.filter(content_type=publication_content_type)


class PublicationPageModelAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = PublicationPage
    menu_label = 'Publications'
    menu_icon = 'doc-full'
    menu_order = 103
    list_display = ('title', 'publishing_date', 'publication_type', 'live', 'publication_series')
    list_filter = ('publishing_date', 'publication_type', 'live', 'publication_series')
    search_fields = ('title',)
    ordering = ['-publishing_date']
    permission_helper_class = CIGIModelAdminPermissionHelper

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(publishing_date__isnull=False)


modeladmin_register(PublicationPageModelAdmin)
