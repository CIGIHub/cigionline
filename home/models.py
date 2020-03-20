from wagtail.core.models import Page


class HomePage(Page):
    """Singleton model for the home page."""

    max_count = 1
    subpage_types = [
        'people.PersonListPage',
        'research.TopicListPage'
    ]
    templates = 'home/home_page.html'

    class Meta:
        verbose_name = 'Home Page'
