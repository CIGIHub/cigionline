from .models import MultimediaPage
from wagtail.contrib.modeladmin.options import (ModelAdmin, modeladmin_register)


class MultimediaPageModelAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = MultimediaPage
    menu_label = 'Multimedia'
    menu_icon = 'media'
    menu_order = 300
    list_display = ('title', 'publishing_date', 'multimedia_type', 'theme', 'live')
    list_filter = ('publishing_date', 'multimedia_type', 'theme', 'live')
    search_fields = ('title',)
    ordering = ['-publishing_date']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(publishing_date__isnull=False)


modeladmin_register(MultimediaPageModelAdmin)
