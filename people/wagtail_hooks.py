from wagtail import hooks
from .models import PersonListPage, PersonPage
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.admin.viewsets.base import ViewSetGroup
from wagtail.admin.ui.tables import Column
from utils.admin_utils import title_with_actions, live_icon, archive_icon, person_types


class PersonPageListingViewSet(ModelViewSet):
    model = PersonPage
    menu_label = 'Staff/Experts'
    menu_icon = 'group'
    menu_order = 101
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
        Column(person_types, label='Person Types', sort_key='person_types'),
        Column('position', label='Position', sort_key='position'),
        Column(archive_icon, label='Archive', sort_key='archive'),
        Column(live_icon, label='Live', sort_key='live'),
        Column('id', label='ID', sort_key='id'),
    ]
    list_filter = ['person_types', 'archive', 'live']
    form_fields = ['title', 'position', 'person_types', 'archive']
    search_fields = ('title',)
    ordering = ['title']


class PersonListPageListingViewSet(ModelViewSet):
    model = PersonListPage
    menu_label = 'Staff/Experts Landing Page'
    menu_icon = 'home'
    menu_order = 100
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    form_fields = ['title',]
    search_fields = ('title',)
    ordering = ['title']


class PersonViewSetGroup(ViewSetGroup):
    menu_label = 'Staff/Experts'
    menu_icon = 'group'
    menu_order = 105
    items = (PersonListPageListingViewSet, PersonPageListingViewSet)


@hooks.register('register_admin_viewset')
def register_person_viewset():
    return PersonViewSetGroup()
