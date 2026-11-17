import datetime
from xml.etree import ElementTree

from django.contrib.auth import get_user_model
from django.utils import timezone
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from articles.models import ArticleListPage, ArticlePage, ArticleTypePage
from home.models import HomePage
from multimedia.models import MultimediaListPage, MultimediaPage
from publications.models import PublicationListPage, PublicationPage, PublicationTypePage


class LatestContentFeedTests(WagtailPageTestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Site.clear_site_root_paths_cache()

    def setUp(self):
        self.user = get_user_model().objects.create_user(username="feed-editor")
        self.site = Site.objects.get(is_default_site=True)
        self.home_page = self._publish(self.site.root_page, HomePage(title="Feed Home"))
        self.site.root_page = self.home_page
        self.site.hostname = "www.cigionline.org"
        self.site.port = 443
        self.site.save()

        self.article_list = self._publish(self.home_page, ArticleListPage(title="Opinions"))
        self.article_type = self._publish(self.article_list, ArticleTypePage(title="Opinion"))
        self.news_type = self._publish(
            self.article_list,
            ArticleTypePage(title="CIGI in the News"),
        )
        self.publication_list = self._publish(
            self.home_page,
            PublicationListPage(title="Publications"),
        )
        self.publication_type = self._publish(
            self.publication_list,
            PublicationTypePage(title="Policy Briefs"),
        )
        self.multimedia_list = self._publish(
            self.home_page,
            MultimediaListPage(title="Multimedia"),
        )

    def _publish(self, parent, page):
        page.owner = self.user
        parent.add_child(instance=page)
        page.save_revision(user=self.user).publish()
        return page

    def _item_titles(self, response):
        root = ElementTree.fromstring(response.content)
        return [item.findtext("title") for item in root.findall("./channel/item")]

    def test_feed_contains_requested_content_types_newest_first(self):
        now = timezone.now()
        article = self._publish(
            self.article_list,
            ArticlePage(
                title="Feed Article",
                article_type=self.article_type,
                publishing_date=now - datetime.timedelta(days=3),
                short_description="<b>Article summary</b>",
            ),
        )
        self._publish(
            self.publication_list,
            PublicationPage(
                title="Feed Publication",
                publication_type=self.publication_type,
                publishing_date=now - datetime.timedelta(days=2),
            ),
        )
        self._publish(
            self.multimedia_list,
            MultimediaPage(
                title="Feed Multimedia",
                publishing_date=now - datetime.timedelta(days=1),
            ),
        )

        response = self.client.get("/feed/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("application/rss+xml"))
        self.assertEqual(
            self._item_titles(response),
            ["Feed Multimedia", "Feed Publication", "Feed Article"],
        )
        root = ElementTree.fromstring(response.content)
        article_item = root.findall("./channel/item")[2]
        self.assertEqual(root.findtext("./channel/ttl"), "15")
        self.assertEqual(article_item.findtext("guid"), f"urn:cigionline:content:{article.pk}")
        self.assertEqual(article_item.find("guid").attrib, {"isPermaLink": "false"})
        self.assertContains(response, "Article summary")
        self.assertNotContains(response, "&lt;b&gt;Article summary&lt;/b&gt;")

    def test_feed_excludes_future_draft_external_news_and_unroutable_items(self):
        now = timezone.now()
        self._publish(
            self.multimedia_list,
            MultimediaPage(
                title="Future Multimedia",
                publishing_date=now + datetime.timedelta(days=1),
            ),
        )
        self._publish(
            self.article_list,
            ArticlePage(
                title="External News",
                article_type=self.news_type,
                publishing_date=now,
            ),
        )
        self.article_list.add_child(
            instance=ArticlePage(
                title="Draft Article",
                article_type=self.article_type,
                publishing_date=now,
                live=False,
                owner=self.user,
            ),
        )
        unroutable = self._publish(
            self.publication_list,
            PublicationPage(
                title="Unroutable Publication",
                publication_type=self.publication_type,
                publishing_date=now,
            ),
        )
        Page.objects.filter(pk=unroutable.pk).update(url_path="/stale-path/")

        response = self.client.get("/feed/")

        self.assertEqual(self._item_titles(response), [])
