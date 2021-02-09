from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse
from django.shortcuts import render

from wagtail.core.models import Page
from wagtail.search.models import Query

from .search import cigi_search


def search(request):  # pragma: no cover
    search_query = request.GET.get('query', None)
    page = request.GET.get('page', 1)

    # Search
    if search_query:
        search_results = Page.objects.live().search(search_query)
        query = Query.get(search_query)

        # Record hit
        query.add_hit()
    else:
        search_results = Page.objects.none()

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return render(request, 'search/search.html', {
        'search_query': search_query,
        'search_results': search_results,
    })


def search_api(request):
    pages = cigi_search(
        contenttypes=request.GET.getlist('contenttype', None),
        contentsubtypes=request.GET.getlist('contentsubtype', None),
        searchtext=request.GET.get('searchtext', None),
        topics=request.GET.getlist('topic', None),
    )
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

    fields = request.GET.getlist('field', [])

    items = []
    for page in pages[offset:offsetLimit]:
        item = {
            'title': page.title,
            'url': page.url,
        }
        for field in fields:
            if field == 'authors':
                item['authors'] = [{
                    'id': author.author.id,
                    'title': author.author.title,
                    'url': author.author.url,
                } for author in page.specific.authors.all()]
            elif field == 'topics':
                item['topics'] = [{
                    'id': topic.id,
                    'title': topic.title,
                    'url': topic.url,
                } for topic in page.specific.topics.all()]
            else:
                item[field] = getattr(page.specific, field)
        items.append(item)

    return JsonResponse({
        'meta': {
            'total_count': pages.count(),
        },
        'items': items,
    }, safe=False)
