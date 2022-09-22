from wagtail.contrib.modeladmin.options import (ModelAdmin, modeladmin_register)
from .models import PublishEmailNotification


class PublishEmailNotificationModelAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = PublishEmailNotification
    menu_label = 'Publish Email Notifications'
    menu_icon = 'date'
    menu_order = 204
    list_display = ('user',)


modeladmin_register(PublishEmailNotificationModelAdmin)
