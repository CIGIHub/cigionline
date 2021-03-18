from publications.models import PublicationPage
from wagtail.contrib.modeladmin.options import (ModelAdmin, modeladmin_register)


class PublicationPageModelAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = PublicationPage
    menu_label = 'Publications'
    menu_icon = 'doc-full'
    menu_order = 103
    list_display = ('title', 'publishing_date', 'publication_type', 'live', 'publication_series')
    list_filter = ('publishing_date', 'publication_type', 'live', 'publication_series')
    search_fields = ('title')
    ordering = ['-publishing_date']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(publishing_date__isnull=False)


modeladmin_register(PublicationPageModelAdmin)
