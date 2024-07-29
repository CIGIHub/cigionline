from core.helpers import CIGIModelAdminPermissionHelper
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from wagtail import hooks

from .models import NewsletterPage


@hooks.register('register_permissions')
def register_newsletter_page_permissions():
    newsletter_content_type = ContentType.objects.get(app_label='newsletters', model='newsletterpage')
    return Permission.objects.filter(content_type=newsletter_content_type)


class NewsletterPageModelAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = NewsletterPage
    menu_label = 'Newsletters'
    menu_icon = 'mail'
    menu_order = 200
    list_display = ('title', 'live', 'html_file', 'latest_revision_created_at')
    list_filter = ('live', 'latest_revision_created_at')
    search_fields = ('title',)
    ordering = ('-latest_revision_created_at',)
    permission_helper_class = CIGIModelAdminPermissionHelper


modeladmin_register(NewsletterPageModelAdmin)
