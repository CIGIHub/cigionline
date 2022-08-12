from newsletters.models import NewsletterPage
from wagtail.core.models import Page
from wagtail.search.backends import get_search_backend
from wagtail.search.backends.elasticsearch7 import (
    Elasticsearch7SearchResults
)

import shlex


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
            body['aggregations'] = {
                "topics_contentpage": {
                    "terms": {
                        "field": "core_contentpage__topics_filter",
                        "size": 50,
                    }
                },
                "topics_personpage": {
                    "terms": {
                        "field": "people_personpage__topics_filter",
                        "size": 50,
                    }
                },
                "years": {
                    "date_histogram": {
                        "field": "core_contentpage__publishing_date_filter",
                        "calendar_interval": "year",
                        "format": "yyyy",
                    }
                },
                "contenttypes": {
                    "terms": {
                        "field": "core_contentpage__contenttype_filter",
                        "size": 50,
                    }
                },
                "contentsubtypes": {
                    "terms": {
                        "field": "core_contentpage__contentsubtype_filter",
                        "size": 50,
                    }
                },
                "content_types": {
                    "terms": {
                        "field": "content_type",
                        "size": 50,
                    }
                },
                "event_access": {
                    "terms": {
                        "field": "events_eventpage__event_access_filter",
                        "size": "50"
                    }
                },
                "experts": {
                    "terms": {
                        "field": "core_contentpage__author_ids_filter",
                        "size": 50,
                    }
                }
            }

        return body

    def get_aggregations(self):
        params = {
            'index': self.backend.get_index_for_model(self.query_compiler.queryset.model).name,
            'body': self._get_es_body(),
            '_source': False,
            self.fields_param_name: 'pk',
        }

        search_results = self.backend.es.search(**params)
        aggregations = search_results['aggregations']

        def bucket_map(val):
            k = 'key'
            if 'key_as_string' in val.keys():
                k = 'key_as_string'
            return {'key': val[k], 'value': val['doc_count']}

        aggs = {}
        for key, value in aggregations.items():
            temp = list(map(bucket_map, value['buckets']))
            aggs[key] = {}
            for item in temp:
                aggs[key][item['key']] = item['value']

        return aggs

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
        self,
        content_type,
        sort,
        contenttypes,
        contentsubtypes,
        authors,
        projects,
        topics,
        searchtext,
        articletypeid,
        publicationtypeid,
        publicationseriesid,
        multimediaseriesid,
        years,
        eventaccess,
        experts,
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
        self.eventaccess = None
        self.experts = None

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
        if experts and len(experts) > 0:
            self.experts = experts
        if articletypeid is not None:
            self.articletypeid = articletypeid
        if publicationtypeid is not None:
            self.publicationtypeid = publicationtypeid
        if publicationseriesid is not None:
            self.publicationseriesid = publicationseriesid
        if multimediaseriesid is not None:
            self.multimediaseriesid = multimediaseriesid
        if eventaccess is not None:
            self.eventaccess = eventaccess
        if years is not None:
            self.years = years

    @property
    def queryset(self):
        return Page.objects.not_type(NewsletterPage).live()

    def get_query(self):
        if self.searchtext:
            try:
                search_list = shlex.split(self.searchtext, posix=False)
            except ValueError:
                search_list = self.searchtext.split()
            terms = []
            should = []
            for item in search_list:
                if item.startswith('"') and item.endswith('"'):
                    should.append({
                        "multi_match": {
                            "fields": ["title", "*__body", "core_contentpage__author_names^2", "*__topic_names^2", "research_topicpage__topic_name^100", "people_personpage__person_name^100"],
                            "query": item,
                            "type": "phrase",
                        },
                    })
                else:
                    terms.append(item)
            should.append({
                "multi_match": {
                    "fields": ["title", "*_body", "core_contentpage__author_names", "*__topic_names^2"],
                    "query": ' '.join(terms),
                },
            },)

            must = {
                "bool": {
                    "should": should
                }
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
        }, {
            "bool": {
                "should": [{
                    "term": {
                        "core_contentpage__exclude_from_search_filter": False,
                    },
                }, {
                    "term": {
                        "core_basicpage__exclude_from_search_filter": False,
                    },
                }, {
                    "term": {
                        "core_privacynoticepage__exclude_from_search_filter": False,
                    },
                }, {
                    "term": {
                        "articles_articlelandingpage__exclude_from_search_filter": False,
                    },
                }, {
                    "term": {
                        "events_eventlistpage__exclude_from_search_filter": False,
                    },
                }, {
                    "term": {
                        "multimedia_multimedialistpage__exclude_from_search_filter": False,
                    },
                }, {
                    "term": {
                        "publications_publicationlistpage__exclude_from_search_filter": False,
                    },
                }, {
                    "term": {
                        "newsletters_newsletterlistpage__exclude_from_search_filter": False,
                    },
                }, {
                    "term": {
                        "subscribe_subscribepage__exclude_from_search_filter": False,
                    },
                }, {
                    "term": {
                        "people_personlistpage__exclude_from_search_filter": False,
                    },
                }, {
                    "term": {
                        "people_personpage__exclude_from_search_filter": False,
                    },
                }, {
                    "term": {
                        "annual_reports_annualreportpage__exclude_from_search_filter": False,
                    },
                }, {
                    "term": {
                        "annual_reports_annualreportlistpage__exclude_from_search_filter": False,
                    },
                }, {
                    "term": {
                        "careers_jobpostingpage__exclude_from_search_filter": False,
                    },
                }, {
                    "term": {
                        "careers_jobpostinglistpage__exclude_from_search_filter": False,
                    },
                }, {
                    "term": {
                        "research_topicpage__exclude_from_search_filter": False,
                    },
                }],
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
        if self.experts:
            filters.append({
                "terms": {
                    "core_contentpage__author_ids_filter": [self.experts],
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
                "bool": {
                    "must": [
                        {
                            "bool": {
                                "should": [
                                    {
                                        "terms": {
                                            "people_personpage__topics_filter": self.topics,
                                        }
                                    },
                                    {
                                        "terms": {
                                            "core_contentpage__topics_filter": self.topics,
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
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
        if self.eventaccess:
            filters.append({
                "terms": {
                    "events_eventpage__event_access_filter": self.eventaccess,
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
            "function_score": {
                "query": {
                    "bool": {
                        "must": must,
                        "filter": filters,
                    },
                },
                "functions": [
                    {
                        "filter": {"terms": {"core_contentpage__contentsubtype_filter": ["CIGI in the News", "News Releases"]}},
                        "weight": 0.25,
                    }
                ],
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


def cigi_search(content_type=None,
                sort=None,
                contenttypes=None,
                contentsubtypes=None,
                authors=None,
                projects=None,
                topics=None,
                searchtext=None,
                articletypeid=None,
                publicationtypeid=None,
                publicationseriesid=None,
                multimediaseriesid=None,
                years=None,
                eventaccess=None,
                experts=None,):
    return CIGIOnlineElasticsearchResults(
        get_search_backend(),
        CIGIOnlineSearchQueryCompiler(content_type,
                                      sort,
                                      contenttypes,
                                      contentsubtypes,
                                      authors,
                                      projects,
                                      topics,
                                      searchtext,
                                      articletypeid,
                                      publicationtypeid,
                                      publicationseriesid,
                                      multimediaseriesid,
                                      years,
                                      eventaccess,
                                      experts,)
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
        self,
        content_type,
        sort,
        contenttypes,
        contentsubtypes,
        authors,
        projects,
        topics,
        searchtext,
        articletypeid,
        publicationtypeid,
        publicationseriesid,
        multimediaseriesid,
        experts,
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
        self.experts = None

        if contenttypes and len(contenttypes) > 0:
            self.contenttypes = contenttypes
        if contentsubtypes and len(contentsubtypes) > 0:
            self.contentsubtypes = contentsubtypes
        if authors and len(authors) > 0:
            self.authors = authors
        if experts and len(experts) > 0:
            self.experts = experts
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
        return Page.objects.not_type(NewsletterPage).live()

    def get_query(self):
        if self.searchtext:
            must = {
                "multi_match": {
                    "fields": ["*__search_terms^100"],
                    "query": self.searchtext,
                    "type": "phrase_prefix",
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
        },
            {
            "bool": {
                "should": [{
                    "term": {
                        "core_contentpage__exclude_from_search_filter": False,
                    },
                }, {
                    "term": {
                        "annual_reports_annualreportpage__exclude_from_search_filter": False,
                    },
                }],
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
        if self.experts:
            filters.append({
                "terms": {
                    "core_contentpage__author_ids_filter": [self.experts],
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


def cigi_search_promoted(content_type=None,
                         sort=None,
                         contenttypes=None,
                         contentsubtypes=None,
                         authors=None,
                         projects=None,
                         topics=None,
                         searchtext=None,
                         articletypeid=None,
                         publicationtypeid=None,
                         publicationseriesid=None,
                         multimediaseriesid=None,
                         experts=None):
    return CIGIOnlineElevatedElasticsearchResults(
        get_search_backend(),
        CIGIOnlineElevatedSearchQueryCompiler(content_type,
                                              sort,
                                              contenttypes,
                                              contentsubtypes,
                                              authors,
                                              projects,
                                              topics,
                                              searchtext,
                                              articletypeid,
                                              publicationtypeid,
                                              publicationseriesid,
                                              multimediaseriesid,
                                              experts)
    )
