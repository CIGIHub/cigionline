from .models import PublishEmailNotification
from wagtail import hooks
from wagtail.admin.ui.tables import Column
from utils.admin_utils import title_with_actions
from wagtail.snippets.views.snippets import SnippetViewSet


class PublishEmailNotificationViewSet(SnippetViewSet):
    model = PublishEmailNotification
    menu_label = 'Publish Email Notifications'
    menu_icon = 'date'
    menu_order = 204
    list_display = [
        Column(title_with_actions, label='User', sort_key='user'),
    ]
    form_fields = ['user', 'email_template']
    search_fields = ('user__username',)
    ordering = ['-user']
    add_to_admin_menu = True


@hooks.register('register_admin_viewset')
def register_publish_email_notification_viewset():
    return PublishEmailNotificationViewSet()
