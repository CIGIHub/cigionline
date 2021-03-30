from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from wagtail.contrib.modeladmin.helpers import PagePermissionHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks

from .models import TopicPage


@hooks.register('register_permissions')
def register_topic_page_permissions():
    topic_content_type = ContentType.objects.get(app_label='research', model='topicpage')
    return Permission.objects.filter(content_type=topic_content_type)


class TopicPageModelAdminPermissionHelper(PagePermissionHelper):
    def user_can_list(self, user):
        return self.user_has_any_permissions(user)


class TopicPageModelAdmin(ModelAdmin):
    model = TopicPage
    menu_label = 'Topics'
    menu_icon = 'thumbtack'
    menu_order = 106
    list_display = ('title')
    list_filter = ('live')
    search_fields = ('title')
    order = ['title']
    permission_helper_class = TopicPageModelAdminPermissionHelper


modeladmin_register(TopicPageModelAdmin)
