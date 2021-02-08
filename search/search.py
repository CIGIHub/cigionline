from wagtail.core.models import Page
from wagtail.search.backends import get_search_backend
from wagtail.search.backends.elasticsearch7 import (
    Elasticsearch7SearchResults
)


class CIGIOnlineSearchQueryCompiler:
    def __init__(
        self, content_type=None, contenttypes=None, contentsubtypes=None, topics=None
    ):
        if content_type is None:
            content_type = 'wagtailcore.Page'
        self.content_type = content_type
        self.contenttypes = None
        self.contentsubtypes = None
        self.topics = None

        if contenttypes and len(contenttypes) > 0:
            self.contenttypes = contenttypes
        if contentsubtypes and len(contentsubtypes) > 0:
            self.contentsubtypes = contentsubtypes
        if topics and len(topics) > 0:
            self.topics = topics

    @property
    def queryset(self):
        return Page.objects.live()

    def get_query(self):
        filters = [{
            "term": {
                "live_filter": True,
            },
        }, {
            "terms": {
                "content_type": [self.content_type],
            },
        }]
        if self.contenttypes:
            filters.append({
                "terms": {
                    "core_contentpage__contenttype_filter": self.contenttypes,
                },
            })
        if self.topics:
            filters.append({
                "terms": {
                    "core_contentpage__topics_filter": self.topics,
                },
            })
        return {
            "bool": {
                "filter": filters,
            },
        }

    def get_sort(self):
        return [{
            "core_contentpage__publishing_date_filter": {
                "order": "desc",
            },
        }]


def cigi_search(content_type=None, contenttypes=None, contentsubtypes=None, topics=None):
    return Elasticsearch7SearchResults(
        get_search_backend(),
        CIGIOnlineSearchQueryCompiler(content_type, contenttypes, contentsubtypes, topics)
    )
