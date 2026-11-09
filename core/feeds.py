from django.contrib.syndication.views import Feed
from django.db.models import Q
from django.utils import timezone
from django.utils.html import strip_tags
from wagtail.models import Site

from core.models import ContentPage


class LatestContentFeed(Feed):
    title = "CIGI — Latest Research and Analysis"
    link = "/"
    description = "The latest articles, publications, and multimedia from CIGI."
    ttl = "15"
    item_guid_is_permalink = False

    def get_object(self, request):
        self.request = request
        return Site.find_for_request(request)

    def items(self, site):
        items = (
            ContentPage.objects.live()
            .public()
            .descendant_of(site.root_page)
            .filter(
                Q(articlepage__isnull=False)
                | Q(publicationpage__isnull=False)
                | Q(multimediapage__isnull=False),
                publishing_date__isnull=False,
                publishing_date__lte=timezone.now(),
            )
            .exclude(articlepage__article_type__title="CIGI in the News")
            .specific()
            .prefetch_related("authors__author", "topics")
            .order_by("-publishing_date")[:50]
        )
        return [item for item in items if item.get_url(request=self.request, current_site=site)]

    def item_description(self, item):
        return strip_tags(item.short_description)

    def item_link(self, item):
        return item.get_url(request=self.request)

    def item_guid(self, item):
        return f"urn:cigionline:content:{item.pk}"

    def item_pubdate(self, item):
        return item.publishing_date

    def item_author_name(self, item):
        return ", ".join(item.author_names)

    def item_categories(self, item):
        return item.topic_names
