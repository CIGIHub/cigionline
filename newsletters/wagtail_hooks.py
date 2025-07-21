from wagtail import hooks
from .models import NewsletterPage
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.admin.ui.tables import Column
from utils.admin_utils import title_with_actions, live_icon


class NewsletterPageListingViewSet(ModelViewSet):
    model = NewsletterPage
    menu_label = 'Newsletters'
    menu_icon = 'mail'
    menu_order = 200
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
        Column(live_icon, label='Live', sort_key='live'),
        Column('latest_revision_created_at', label='Latest Draft Created At', sort_key='latest_revision_created_at'),
    ]
    list_filter = ['live', 'latest_revision_created_at']
    form_fields = ['title',]
    search_fields = ('title',)
    ordering = ['-latest_revision_created_at']
    add_to_admin_menu = True


@hooks.register('register_admin_viewset')
def register_newsletter_viewset():
    return NewsletterPageListingViewSet()
