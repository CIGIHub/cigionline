from wagtail.core.fields import RichTextField
from wagtail.core.models import Page


class HomePage(Page):
    """Singleton model for the home page."""

    max_count = 1
    subpage_types = [
        'people.PersonListPage',
        'research.TopicListPage'
    ]
    templates = 'core/home_page.html'

    class Meta:
        verbose_name = 'Home Page'


class CorePage(Page):
    """Page with subtitle."""

    subtitle = RichTextField(blank=True, null=False, features=['bold', 'italic'])

    class Meta:
        abstract = True
