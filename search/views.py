from django.http import JsonResponse
from django.shortcuts import render
from wagtail.contrib.search_promotions.models import Query

from .search import cigi_search, cigi_search_promoted


def process_item(page, request):
    try:
        snippet = page.specific.body_snippet
    except AttributeError:
        snippet = ''
    fields = request.GET.getlist('field', [])
    item = {
        'highlights': page._highlights,
        'elevated': page._elevated,
        'id': page.id,
        'title': page.title,
        'url': page.get_url(request),
        'snippet': snippet,
    }
    for field in fields:
        try:
            if field == 'authors':
                item['authors'] = [{
                    'id': author.author.id,
                    'title': author.author.title,
                    'url': author.author.url,
                } for author in page.specific.authors.all()]
            elif field == 'series_authors':
                item['series_authors'] = [{
                    'id': author.id,
                    'title': author.title,
                    'url': author.url,
                } for author in page.specific.series_authors]
            elif field == 'cigi_people_mentioned':
                item['cigi_people_mentioned'] = [{
                    'id': person.person.id,
                    'title': person.person.title,
                    'url': person.person.url,
                } for person in page.specific.cigi_people_mentioned.all()]
            elif field == 'topics':
                item['topics'] = [{
                    'id': topic.id,
                    'title': topic.title,
                    'url': topic.url,
                } for topic in page.specific.topics.all()]
            elif field == 'countries':
                item['countries'] = [{
                    'id': country.id,
                    'title': country.title,
                    'url': country.url,
                } for country in page.specific.countries.all()]
            elif field == 'contenttype':
                verbose_name = page.specific._meta.verbose_name
                if verbose_name == 'Person Page':
                    item['contenttype'] = 'Person'
                elif verbose_name == 'Topic Page':
                    item['contenttype'] = 'Topic'
                elif verbose_name == 'Publication Series':
                    item['contenttype'] = verbose_name
                else:
                    item['contenttype'] = getattr(page.specific, field)
            else:
                item[field] = getattr(page.specific, field)
        except AttributeError:
            pass
    return item


def search(request):  # pragma: no cover
    return render(request, 'search/search.html')


def search_api(request):
    searchtext = request.GET.get('searchtext', None)
    if searchtext:
        query = Query.get(searchtext)

        # Record hit
        query.add_hit()
    elif request.GET.get('searchpage'):
        return JsonResponse({
            'meta': {
                'total_count': 0,
                'aggregations': {
                    'topics': {},
                    'contenttypes': {},
                    'contentsubtypes': {},
                    'years': {},
                    'content_types': {},
                    'experts': {},
                }
            },
            'items': [],
        }, safe=False)
    pages = cigi_search(
        articletypeid=request.GET.get('articletypeid', None),
        authors=request.GET.getlist('author', None),
        content_type=request.GET.get('content_type', None),
        contenttypes=request.GET.getlist('contenttype', None),
        contentsubtypes=request.GET.getlist('contentsubtype', None),
        multimediaseriesid=request.GET.get('multimediaseriesid', None),
        opinionseriesid=request.GET.get('opinionseriesid', None),
        projects=request.GET.getlist('project', None),
        publicationseriesid=request.GET.get('publicationseriesid', None),
        publicationtypeid=request.GET.get('publicationtypeid', None),
        searchtext=searchtext,
        sort=request.GET.get('sort', None),
        topics=request.GET.getlist('topic', None),
        years=request.GET.getlist('year', None),
        eventaccess=request.GET.getlist('eventaccess', None),
        experts=request.GET.get('expert', None),
        countries=request.GET.getlist('country', None),
        exclusions=request.GET.getlist('exclusions', None),
        additional_authored_pages=request.GET.get('additional_authored_pages', None),
    )
    promoted_pages = []
    if request.GET.get('searchpage'):
        promoted_pages = cigi_search_promoted(
            articletypeid=request.GET.get('articletypeid', None),
            authors=request.GET.getlist('author', None),
            content_type=request.GET.get('content_type', None),
            contenttypes=request.GET.getlist('contenttype', None),
            contentsubtypes=request.GET.getlist('contentsubtype', None),
            multimediaseriesid=request.GET.get('multimediaseriesid', None),
            opinionseriesid=request.GET.get('opinionseriesid', None),
            projects=request.GET.getlist('project', None),
            publicationseriesid=request.GET.get('publicationseriesid', None),
            publicationtypeid=request.GET.get('publicationtypeid', None),
            searchtext=searchtext,
            sort=request.GET.get('sort', None),
            topics=request.GET.getlist('topic', None),
            experts=request.GET.get('expert', None),
            countries=request.GET.getlist('country', None),
            exclusions=request.GET.getlist('exclusions', None),
        )

    aggregations = pages.get_aggregations()

    default_limit = 24
    default_offset = 0
    limit = request.GET.get('limit', default_limit)
    if limit is not None and limit.isnumeric():
        limit = int(limit)
    else:
        limit = default_limit
    offset = request.GET.get('offset', default_offset)
    if offset is not None and offset.isnumeric():
        offset = int(offset)
    else:
        offset = default_offset
    offsetLimit = limit + offset

    items = []
    for page in promoted_pages:
        items.append(process_item(page, request))
    for page in pages[offset:offsetLimit]:
        items.append(process_item(page, request))

    return JsonResponse({
        'meta': {
            'total_count': pages.count(),
            'aggregations': aggregations
        },
        'items': items,
    }, safe=False)
