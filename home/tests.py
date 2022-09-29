from articles.models import (
    ArticleLandingPage,
    ArticleListPage,
    ArticleSeriesListPage,
    ArticleSeriesPage,
    MediaLandingPage,
)
from careers.models import JobPostingListPage
from contact.models import ContactPage
from core.models import (
    BasicPage,
    PrivacyNoticePage,
)
from events.models import EventListPage
from features.models import FeaturesListPage
from multimedia.models import MultimediaListPage, MultimediaSeriesListPage, MultimediaSeriesPage
from newsletters.models import NewsletterListPage
from people.models import PeoplePage, PersonListPage
from publications.models import PublicationListPage, PublicationSeriesListPage
from research.models import (
    ProjectListPage,
    ResearchLandingPage,
    TopicListPage,
)
from subscribe.models import SubscribePage
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTests
from wagtail.test.utils.form_data import nested_form_data

from .models import HomePage


class HomePageTests(WagtailPageTests):
    def test_homepage_child_page_types(self):
        """
        Verify allowed child page types.
        """
        self.assertAllowedSubpageTypes(
            HomePage,
            {
                ArticleLandingPage,
                ArticleListPage,
                ArticleSeriesListPage,
                ArticleSeriesPage,
                BasicPage,
                ContactPage,
                EventListPage,
                FeaturesListPage,
                JobPostingListPage,
                MediaLandingPage,
                MultimediaListPage,
                MultimediaSeriesListPage,
                MultimediaSeriesPage,
                NewsletterListPage,
                PeoplePage,
                PersonListPage,
                PrivacyNoticePage,
                ProjectListPage,
                PublicationListPage,
                PublicationSeriesListPage,
                ResearchLandingPage,
                SubscribePage,
                TopicListPage,
            }
        )

    def test_cannot_create_homepage(self):
        """
        Test that we can't create a second home page. Wagtail will create a home
        page object on initialization so we don't need to create one first.
        """
        root_page = Page.objects.get(pk=1)
        try:
            self.assertCanCreate(root_page, HomePage, nested_form_data({
                'title': 'Home',
            }))
            self.fail('Expected to error')
        except AssertionError:
            pass
