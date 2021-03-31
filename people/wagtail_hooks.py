from .models import PersonPage, PersonListPage
from wagtail.contrib.modeladmin.options import (ModelAdmin, modeladmin_register, ModelAdminGroup)


class PersonListPageAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = PersonListPage
    menu_label = 'People List Pages'
    menu_icon = 'group'
    menu_order = 100
    list_display = ('title',)


class PersonPageAdmin(ModelAdmin):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    model = PersonPage
    menu_label = 'People'
    menu_icon = 'group'
    menu_order = 101
    list_display = ('title', 'get_person_type', 'latest_revision_created_at', 'archive', 'live')
    list_filter = ('latest_revision_created_at', 'person_types__name', 'archive', 'live')
    search_fields = ('title',)
    ordering = ['-latest_revision_created_at']

    def get_person_type(self, person):
        return [person_type.name for person_type in person.person_types.all()]
    get_person_type.short_description = 'Person Types'
    get_person_type.admin_order_field = 'person_types__name'


class PeopleGroup(ModelAdminGroup):
    # See https://docs.wagtail.io/en/stable/reference/contrib/modeladmin/
    menu_label = 'People'
    menu_icon = 'group'
    menu_order = 200
    items = (PersonListPageAdmin, PersonPageAdmin)


modeladmin_register(PeopleGroup)
