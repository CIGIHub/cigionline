from wagtail.search.backends import get_search_backend
from wagtail.search.backends.elasticsearch7 import (
    Elasticsearch7SearchResults
)

from .models import PersonPage


class CIGIOnlineExpertsSearchQueryCompiler:
    def __init__(self, searchtext):
        self.searchtext = searchtext

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
                "people_personpage__archive": 0,
            },
        }, {
            "terms": {
                "people_personpage__person_types_filter": ["CIGI Chair", "Expert"],
            },
        }]

        return {
            "bool": {
                "must": must,
                "filter": filters,
            },
        }

    def get_sort(self):
        return [{
            "people_personpage__last_name_lowercase_filter": {
                "order": "asc",
            },
        }, {
            "people_personpage__first_name_lowercase_filter": {
                "order": "asc",
            },
        }]


def experts_search(searchtext=None):
    return Elasticsearch7SearchResults(
        get_search_backend(),
        CIGIOnlineExpertsSearchQueryCompiler(searchtext),
    )
