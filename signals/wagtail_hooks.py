from .models import PublishEmailNotification
from wagtail import hooks
from wagtail.admin.ui.tables import Column
from utils.admin_utils import title_with_actions
from wagtail.admin.viewsets.model import ModelViewSet


class PublishEmailNotificationViewSet(ModelViewSet):
    model = PublishEmailNotification
    menu_label = 'Publish Email Notifications'
    menu_icon = 'date'
    icon = 'date'
    menu_order = 204
    list_display = [
        Column(title_with_actions, label='User', sort_key='user'),
    ]
    exclude_form_fields = []
    search_fields = ('user__username',)
    ordering = ['-user']
    add_to_admin_menu = True


@hooks.register('register_admin_viewset')
def register_publish_email_notification_viewset():
    return PublishEmailNotificationViewSet()
