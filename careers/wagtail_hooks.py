from wagtail import hooks
from .models import JobPostingListPage, JobPostingPage
from utils.admin_utils import title_with_actions, live_icon
from wagtail.admin.viewsets.pages import PageListingViewSet
from wagtail.admin.viewsets.base import ViewSetGroup
from wagtail.admin.ui.tables import Column


class JobPostingPageListingViewSet(PageListingViewSet):
    model = JobPostingPage
    menu_label = 'Job Postings'
    menu_icon = 'user'
    menu_order = 101
    name = 'jobpostingpage'
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
        Column('latest_revision_created_at', label='Latest Draft Created At', sort_key='latest_revision_created_at'),
        Column(live_icon, label='Live', sort_key='live'),
        Column('id', label='ID', sort_key='id'),
    ]
    list_filter = ['live']
    search_fields = ('title',)
    ordering = ['-latest_revision_created_at', 'title']


class JobPostingListPageListingViewSet(PageListingViewSet):
    model = JobPostingListPage
    menu_label = 'Careers Landing Page'
    menu_icon = 'home'
    menu_order = 100
    name = 'jobpostinglistpage'
    list_display = [
        Column(title_with_actions, label='Title', sort_key='title'),
    ]
    search_fields = ('title',)
    ordering = ['title']


class JobPostingViewSetGroup(ViewSetGroup):
    menu_label = 'Careers'
    menu_icon = 'user'
    menu_order = 202
    items = (JobPostingListPageListingViewSet, JobPostingPageListingViewSet)


@hooks.register('register_admin_viewset')
def register_job_posting_viewset():
    return JobPostingViewSetGroup()
