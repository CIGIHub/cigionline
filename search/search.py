from wagtail.core.models import Page
from wagtail.search.backends import get_search_backend
from wagtail.search.backends.elasticsearch7 import (
    Elasticsearch7SearchResults
)


class CIGIOnlineElasticsearchResults(Elasticsearch7SearchResults):
    def _get_es_body(self, for_count=False):
        body = super()._get_es_body(for_count)

        if not for_count:
            body["highlight"] = {
                "fields": {
                    "*__body": {},
                },
                "fragment_size": 256,
            }
        return body

    def _get_results_from_hits(self, hits):
        """
        Yields Django model instances from a page of hits returned by Elasticsearch
        """
        # Get pks from results
        pks = [hit['fields']['pk'][0] for hit in hits]
        scores = {str(hit['fields']['pk'][0]): hit['_score'] for hit in hits}
        highlights = {}

        for hit in hits:
            highlight = hit.get('highlight', None)
            if highlight is not None:
                highlights[str(hit['fields']['pk'][0])] = [item for key, value in highlight.items() for item in highlight[key]]
            else:
                highlights[str(hit['fields']['pk'][0])] = []

        # Initialise results dictionary
        results = {str(pk): None for pk in pks}

        # Find objects in database and add them to dict
        for obj in self.query_compiler.queryset.filter(pk__in=pks):
            results[str(obj.pk)] = obj

            if self._score_field:
                setattr(obj, self._score_field, scores.get(str(obj.pk)))

            setattr(obj, '_highlights', highlights.get(str(obj.pk)))
            setattr(obj, '_elevated', False)

        # Yield results in order given by Elasticsearch
        for pk in pks:
            result = results[str(pk)]
            if result:
                yield result


class CIGIOnlineSearchQueryCompiler:
    def __init__(
        self, content_type, sort, contenttypes, contentsubtypes, authors, projects, topics, searchtext, articletypeid, publicationtypeid, publicationseriesid, multimediaseriesid, years
    ):
        if content_type is None:
            content_type = 'wagtailcore.Page'
        self.content_type = content_type
        self.sort = sort
        self.contenttypes = None
        self.contentsubtypes = None
        self.authors = None
        self.projects = None
        self.topics = None
        self.searchtext = searchtext
        self.articletypeid = None
        self.publicationtypeid = None
        self.publicationseriesid = None
        self.multimediaseriesid = None
        self.years = None

        if contenttypes and len(contenttypes) > 0:
            self.contenttypes = contenttypes
        if contentsubtypes and len(contentsubtypes) > 0:
            self.contentsubtypes = contentsubtypes
        if authors and len(authors) > 0:
            self.authors = authors
        if projects and len(projects) > 0:
            self.projects = projects
        if topics and len(topics) > 0:
            self.topics = topics
        if articletypeid is not None:
            self.articletypeid = articletypeid
        if publicationtypeid is not None:
            self.publicationtypeid = publicationtypeid
        if publicationseriesid is not None:
            self.publicationseriesid = publicationseriesid
        if multimediaseriesid is not None:
            self.multimediaseriesid = multimediaseriesid
        if years is not None:
            self.years = years

    @property
    def queryset(self):
        return Page.objects.live()

    def get_query(self):
        if self.searchtext:
            must = {
                "multi_match": {
                    "fields": ["title", "*__body", "core_contentpage__author_names"],
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
                    "core_contentpage__author_ids_filter": self.authors,
                },
            })
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
        if self.publicationseriesid:
            filters.append({
                "term": {
                    "publications_publicationpage__publication_series_id_filter": self.publicationseriesid,
                },
            })
        if self.multimediaseriesid:
            filters.append({
                "term": {
                    "multimedia_multimediapage__multimedia_series_id_filter": self.multimediaseriesid,
                },
            })
        if self.years:
            year_ranges = []
            for year in self.years:
                year_ranges.append({
                    "range": {
                        "core_contentpage__publishing_date_filter": {
                            "gte": f"{year}||/y",
                            "lte": f"{year}||/y",
                            "format": "yyyy"
                        }
                    }
                })
            filters.append({
                    "bool": {
                        "should": year_ranges
                    }
                })

        return {
            "bool": {
                "must": must,
                "filter": filters,
            },
        }

    def get_sort(self):
        if self.sort == 'relevance':
            return []

        return [{
            "core_contentpage__publishing_date_filter": {
                "order": "desc",
            },
        }]


def cigi_search(content_type=None, sort=None, contenttypes=None, contentsubtypes=None, authors=None, projects=None, topics=None, searchtext=None, articletypeid=None, publicationtypeid=None, publicationseriesid=None, multimediaseriesid=None, years=None):
    return CIGIOnlineElasticsearchResults(
        get_search_backend(),
        CIGIOnlineSearchQueryCompiler(content_type, sort, contenttypes, contentsubtypes, authors, projects, topics, searchtext, articletypeid, publicationtypeid, publicationseriesid, multimediaseriesid, years)
    )


class CIGIOnlineElevatedElasticsearchResults(Elasticsearch7SearchResults):
    def _get_es_body(self, for_count=False):
        body = super()._get_es_body(for_count)

        if not for_count:
            body["highlight"] = {
                "fields": {
                    "*__search_terms": {}
                },
                "fragment_size": 256,
            }
        return body

    def _get_results_from_hits(self, hits):
        """
        Yields Django model instances from a page of hits returned by Elasticsearch
        """
        # Get pks from results
        pks = [hit['fields']['pk'][0] for hit in hits]
        scores = {str(hit['fields']['pk'][0]): hit['_score'] for hit in hits}
        highlights = {}
        elevated = {}

        for hit in hits:
            highlight = hit.get('highlight', None)
            if highlight is not None:
                if '__search_terms' in "".join(highlight.keys()):
                    elevated[str(hit['fields']['pk'][0])] = True
                else:
                    elevated[str(hit['fields']['pk'][0])] = False
                highlights[str(hit['fields']['pk'][0])] = [item for key, value in highlight.items() for item in highlight[key] if '__search_terms' not in key]
            else:
                highlights[str(hit['fields']['pk'][0])] = []

        # Initialise results dictionary
        results = {str(pk): None for pk in pks}

        # Find objects in database and add them to dict
        for obj in self.query_compiler.queryset.filter(pk__in=pks):
            results[str(obj.pk)] = obj

            if self._score_field:
                setattr(obj, self._score_field, scores.get(str(obj.pk)))

            setattr(obj, '_highlights', highlights.get(str(obj.pk)))
            setattr(obj, '_elevated', elevated.get(str(obj.pk)))

        # Yield results in order given by Elasticsearch
        for pk in pks:
            result = results[str(pk)]
            if result:
                yield result


class CIGIOnlineElevatedSearchQueryCompiler:
    def __init__(
        self, content_type, sort, contenttypes, contentsubtypes, authors, projects, topics, searchtext, articletypeid, publicationtypeid, publicationseriesid, multimediaseriesid
    ):
        if content_type is None:
            content_type = 'wagtailcore.Page'
        self.content_type = content_type
        self.sort = sort
        self.contenttypes = None
        self.contentsubtypes = None
        self.authors = None
        self.projects = None
        self.topics = None
        self.searchtext = searchtext
        self.articletypeid = None
        self.publicationtypeid = None
        self.publicationseriesid = None
        self.multimediaseriesid = None
        self.years = None

        if contenttypes and len(contenttypes) > 0:
            self.contenttypes = contenttypes
        if contentsubtypes and len(contentsubtypes) > 0:
            self.contentsubtypes = contentsubtypes
        if authors and len(authors) > 0:
            self.authors = authors
        if projects and len(projects) > 0:
            self.projects = projects
        if topics and len(topics) > 0:
            self.topics = topics
        if articletypeid is not None:
            self.articletypeid = articletypeid
        if publicationtypeid is not None:
            self.publicationtypeid = publicationtypeid
        if publicationseriesid is not None:
            self.publicationseriesid = publicationseriesid
        if multimediaseriesid is not None:
            self.multimediaseriesid = multimediaseriesid

    @property
    def queryset(self):
        return Page.objects.live()

    def get_query(self):
        if self.searchtext:
            must = {
                "multi_match": {
                    "fields": ["*__search_terms^100"],
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
                    "core_contentpage__author_ids_filter": self.authors,
                },
            })
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
        if self.publicationseriesid:
            filters.append({
                "term": {
                    "publications_publicationpage__publication_series_id_filter": self.publicationseriesid,
                },
            })
        if self.multimediaseriesid:
            filters.append({
                "term": {
                    "multimedia_multimediapage__multimedia_series_id_filter": self.multimediaseriesid,
                },
            })

        return {
            "bool": {
                "must": must,
                "filter": filters,
            },
        }

    def get_sort(self):
        return []


def cigi_search_promoted(content_type=None, sort=None, contenttypes=None, contentsubtypes=None, authors=None, projects=None, topics=None, searchtext=None, articletypeid=None, publicationtypeid=None, publicationseriesid=None, multimediaseriesid=None):
    return CIGIOnlineElevatedElasticsearchResults(
        get_search_backend(),
        CIGIOnlineElevatedSearchQueryCompiler(content_type, sort, contenttypes, contentsubtypes, authors, projects, topics, searchtext, articletypeid, publicationtypeid, publicationseriesid, multimediaseriesid)
    )
