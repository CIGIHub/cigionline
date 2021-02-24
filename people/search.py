from core.models import ContentPage
from wagtail.search.backends import get_search_backend
from wagtail.search.backends.elasticsearch7 import (
    Elasticsearch7SearchResults
)

from .models import PersonPage


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
                    "term": {
                        "live_filter": True,
                    },
                }, {
                    "terms": {
                        "content_type": ["core.ContentPage"],
                    },
                }, {
                    "terms": {
                        "core_contentpage__related_people_ids_filter": [self.expert_id],
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


def expert_latest_activity_search(expert_id):
    return Elasticsearch7SearchResults(
        get_search_backend(),
        CIGIOnlineExpertLatestActivitySearchQueryCompiler(expert_id),
    )


class CIGIOnlineExpertsSearchQueryCompiler:
    def __init__(self, searchtext, sort, topics):
        self.searchtext = searchtext
        self.sort = sort
        self.topics = topics

    @property
    def queryset(self):
        return PersonPage.objects.live()

    def get_query(self):
        if self.searchtext:
            must = {
                "multi_match": {
                    "fields": ["title"],
                    "operator": "and",
                    "query": self.searchtext,
                },
            }
        else:
            must = {
                "match_all": {},
            }

        filters = [{
            "term": {
                "live_filter": True,
            },
        }, {
            "terms": {
                "content_type": ["people.PersonPage"],
            },
        }, {
            "term": {
                "people_personpage__archive_filter": 0,
            },
        }, {
            "terms": {
                "people_personpage__person_types_filter": ["CIGI Chair", "Expert"],
            },
        }]
        if self.topics:
            filters.append({
                "terms": {
                    "people_personpage__topics_filter": self.topics,
                },
            })

        return {
            "bool": {
                "must": must,
                "filter": filters,
            },
        }

    def get_sort(self):
        sort = [{
            "people_personpage__last_name_lowercase_filter": {
                "order": "asc",
            },
        }, {
            "people_personpage__first_name_lowercase_filter": {
                "order": "asc",
            },
        }]
        if self.sort == 'first_name':
            sort.reverse()
        return sort


def experts_search(searchtext=None, sort=None, topics=None):
    return Elasticsearch7SearchResults(
        get_search_backend(),
        CIGIOnlineExpertsSearchQueryCompiler(searchtext, sort, topics),
    )
