from articles.models import ArticlePage
from core.models import ContentPage
from wagtail.search.backends import get_search_backend
from wagtail.search.backends.elasticsearch7 import (
    Elasticsearch7SearchResults
)


class CIGIOnlineExpertLatestActivitySearchQueryCompiler:
    def __init__(self, expert_id):
        self.expert_id = expert_id

    @property
    def queryset(self):
        return ContentPage.objects.live()

    def get_query(self):
        return {
            "bool": {
                "filter": [{
                    "bool": {
                        "should": [{
                            "bool": {
                                "must": [{
                                    "term": {
                                        "_django_content_type": "articles.ArticlePage",
                                    },
                                }, {
                                    "terms": {
                                        "core_contentpage__contentsubtype_filter": ["Opinion", "Op-Eds", "CIGI in the News"]
                                    }
                                }]
                            }
                        }, {
                            "bool": {
                                "must": [{
                                    "terms": {
                                        "_django_content_type": ["publications.PublicationPage", "multimedia.MultimediaPage"],
                                    }
                                }]
                            }
                        }],
                    },
                }, {
                    "term": {
                        "live_filter": True,
                    },
                }, {
                    "terms": {
                        "core_contentpage__related_people_ids_filter": [self.expert_id],
                    },
                }],
            }
        }

    def get_sort(self):
        return [{
            "core_contentpage__publishing_date_filter": {
                "order": "desc",
            },
        }]


def expert_latest_activity_search(expert_id):
    return Elasticsearch7SearchResults(
        get_search_backend(),
        CIGIOnlineExpertLatestActivitySearchQueryCompiler(expert_id),
    )


class CIGIOnlineExpertLatestInTheNewsSearchQueryCompiler:
    def __init__(self, expert_id):
        self.expert_id = expert_id

    @property
    def queryset(self):
        return ArticlePage.objects.live()

    def get_query(self):
        return {
            "bool": {
                "filter": [{
                    "term": {
                        "live_filter": True,
                    },
                }, {
                    "terms": {
                        "_django_content_type": ["articles.ArticlePage"],
                    },
                }, {
                    "term": {
                        "core_contentpage__contentsubtype_filter": "CIGI in the News",
                    },
                }, {
                    "terms": {
                        "articles_articlepage__cigi_people_mentioned_ids_filter": [self.expert_id],
                    },
                }],
            },
        }

    def get_sort(self):
        return [{
            "core_contentpage__publishing_date_filter": {
                "order": "desc",
            },
        }]


def expert_latest_in_the_news_search(expert_id):
    return Elasticsearch7SearchResults(
        get_search_backend(),
        CIGIOnlineExpertLatestInTheNewsSearchQueryCompiler(expert_id),
    )
