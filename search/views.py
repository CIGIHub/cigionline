from django.http import JsonResponse
from django.shortcuts import render
from wagtail.contrib.search_promotions.models import Query

from .search import cigi_search, cigi_search_promoted
from core.routers import pager_range


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


def search(request):
    """Resources Router — DS faceted browse over Elasticsearch (cigi_search),
    server-rendered with the shared .ds-router chrome. In-place filtering is
    progressive enhancement: an AJAX request (router.js) gets just the results
    partial; with no JS the GET form full-reloads."""
    from django.core.paginator import Paginator
    from research.models import TopicPage
    from core.models import ContentPage
    from core.routers import is_ajax, router_partial_response

    get = request.GET
    q = (get.get('q') or '').strip()
    topics = [t for t in get.getlist('topic') if t.isdigit()]
    contenttypes = get.getlist('contenttype')
    years = [y for y in get.getlist('year') if y.isdigit() and 1000 <= int(y) <= 9999]

    if q:
        Query.get(q).add_hit()

    # A text query ranks by relevance (ES _score); browsing without one stays
    # newest-first. Without this, get_sort()'s date default buried strong
    # matches under whatever was published last.
    results = cigi_search(
        searchtext=q or None,
        topics=topics or None,
        contenttypes=contenttypes or None,
        years=years or None,
        sort=get.get('sort') or ('relevance' if q else None),
    )

    paginator = Paginator(results, 12)
    # Elasticsearch refuses from+size beyond index.max_result_window (13000
    # here) — deep pages, including Paginator's own last-page clamp on a 13k+
    # result set, 500. Cap the cursor to the deepest ES-servable page.
    max_es_page = (13000 - 12) // 12
    try:
        requested = int(get.get('page') or 1)
    except (TypeError, ValueError):
        requested = 1
    page = paginator.get_page(max(1, min(requested, max_es_page)))
    # ES attaches its highlight fragments (`<em>`-marked body excerpts) to the
    # base Page hit; `.specific` refetches, so carry them across under a
    # template-readable name (a leading underscore is invisible to Django
    # templates). Whole fragments only, to a ~350-char budget — a substring
    # cut can split an <em> tag open.
    items = []
    for p in page.object_list:
        item = p.specific
        fragments, total = [], 0
        for fragment in getattr(p, '_highlights', None) or []:
            if fragments and total + len(fragment) > 350:
                break
            fragments.append(fragment)
            total += len(fragment)
        item.search_highlights = fragments
        items.append(item)

    params = get.copy()
    params.pop('page', None)

    context = {
        'page_title': 'Search Results',
        'router_results': items,
        'router_results_template': 'includes/router_items/resource.html',
        'router_empty': 'No resources match your filters.',
        'router_clear_url': request.path,
        'router_page': page,
        'router_total': paginator.count,
        'router_range_start': page.start_index(),
        'router_range_end': page.end_index(),
        'router_page_range': pager_range(page),  # five-page window + last page (BugHerd #431)
        'router_querystring': params.urlencode(),
        'facet_topics': TopicPage.objects.live().filter(archive=0).order_by('title'),
        'facet_types': ['Publication', 'Opinion', 'Multimedia', 'Event'],
        'facet_years': [d.year for d in (ContentPage.objects.live().public()
                        .exclude(publishing_date__isnull=True)
                        .dates('publishing_date', 'year', order='DESC'))],
        'selected': {'q': q, 'topics': set(topics), 'types': set(contenttypes), 'years': set(years)},
    }
    if is_ajax(request):
        return router_partial_response(request, context)
    return render(request, 'search/search.html', context)


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
        exclusions=request.GET.get('exclusions', None),
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
            exclusions=request.GET.get('exclusions', None),
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
