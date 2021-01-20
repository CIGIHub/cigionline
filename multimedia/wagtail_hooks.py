from wagtail.core import hooks
from .models import MultimediaPage
from wagtail.contrib.modeladmin.options import (ModelAdmin, modeladmin_register)

# See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/

class MultimediaPageModelAdmin(ModelAdmin):
    model = MultimediaPage
    menu_label = 'Multimedia'
    menu_icon = 'media'
    menu_order = 300
    list_display = ('title', 'publishing_date', 'multimedia_type', 'live')
    list_filter = ('publishing_date', 'multimedia_type', 'live')
    search_fields = ('title')

modeladmin_register(MultimediaPageModelAdmin)
