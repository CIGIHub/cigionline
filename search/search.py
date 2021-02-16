from wagtail.core.models import Page
from wagtail.search.backends import get_search_backend
from wagtail.search.backends.elasticsearch7 import (
    Elasticsearch7SearchResults
)


class CIGIOnlineSearchQueryCompiler:
    def __init__(
        self, content_type, contenttypes, contentsubtypes, authors, persontypes, projects, topics, searchtext, articletypeid, publicationtypeid
    ):
        if content_type is None:
            content_type = 'wagtailcore.Page'
        self.content_type = content_type
        self.contenttypes = None
        self.contentsubtypes = None
        self.authors = None
        self.persontypes = None
        self.projects = None
        self.topics = None
        self.searchtext = searchtext
        self.articletypeid = None
        self.publicationtypeid = None

        if contenttypes and len(contenttypes) > 0:
            self.contenttypes = contenttypes
        if contentsubtypes and len(contentsubtypes) > 0:
            self.contentsubtypes = contentsubtypes
        if authors and len(authors) > 0:
            self.authors = authors
        if persontypes and len(persontypes) > 0:
            self.persontypes = persontypes
        if projects and len(projects) > 0:
            self.projects = projects
        if topics and len(topics) > 0:
            self.topics = topics
        if articletypeid is not None:
            self.articletypeid = articletypeid
        if publicationtypeid is not None:
            self.publicationtypeid = publicationtypeid

    @property
    def queryset(self):
        return Page.objects.live()

    def get_query(self):
        if self.searchtext:
            must = {
                "multi_match": {
                    "fields": ["*"],
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
                "content_type": [self.content_type],
            },
        }]
        if self.contenttypes:
            filters.append({
                "terms": {
                    "core_contentpage__contenttype_filter": self.contenttypes,
                },
            })
        if self.contentsubtypes:
            filters.append({
                "terms": {
                    "core_contentpage__contentsubtype_filter": self.contentsubtypes,
                },
            })
        if self.authors:
            filters.append({
                "terms": {
                    "core_contentpage__authors_filter": self.authors,
                },
            })
        if self.persontypes:
            filters.extend([
                {
                    "terms": {
                        "people_personpage__persontypes_filter": self.persontypes,
                    },
                },
                {
                    "terms": {
                        "people_personpage__archive_filter": [0],
                    },
                },
            ])
        if self.projects:
            filters.append({
                "terms": {
                    "core_contentpage__projects_filter": self.projects,
                },
            })
        if self.topics:
            filters.append({
                "terms": {
                    "core_contentpage__topics_filter": self.topics,
                },
            })
        if self.articletypeid:
            filters.append({
                "term": {
                    "articles_articlepage__article_type_id_filter": self.articletypeid,
                },
            })
        if self.publicationtypeid:
            filters.append({
                "term": {
                    "publications_publicationpage__publication_type_id_filter": self.publicationtypeid,
                },
            })

        return {
            "bool": {
                "must": must,
                "filter": filters,
            },
        }

    def get_sort(self):
        if self.content_type == 'people.PersonPage' and 'Staff' in self.persontypes:
            return [{
                "people_personpage__last_name_filter": {
                    "order": "asc",
                },
            }]
        else:
            return [{
                "core_contentpage__publishing_date_filter": {
                    "order": "desc",
                },
            }]


def cigi_search(content_type=None, contenttypes=None, contentsubtypes=None, authors=None, persontypes=None, projects=None, topics=None, searchtext=None, articletypeid=None, publicationtypeid=None):
    return Elasticsearch7SearchResults(
        get_search_backend(),
        CIGIOnlineSearchQueryCompiler(content_type, contenttypes, contentsubtypes, authors, persontypes, projects, topics, searchtext, articletypeid, publicationtypeid)
    )
