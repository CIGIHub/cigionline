from newsletters.models import NewsletterPage
from wagtail.contrib.modeladmin.options import (ModelAdmin, modeladmin_register)


class NewsletterPageModelAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = NewsletterPage
    menu_label = 'Newsletters'
    menu_icon = 'site'
    menu_order = 200
    list_display = ('title', 'live', 'html_file', 'latest_revision_created_at')
    list_filter = ('live', 'latest_revision_created_at')
    search_fields = ('title')
    ordering = ('-latest_revision_created_at',)


modeladmin_register(NewsletterPageModelAdmin)
