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
    return JsonResponse({
        'meta': {
            'total_count': pages.count(),
        },
        'items': [
            {
                'authors': [{
                    'id': author.author.id,
                    'title': author.author.title,
                    'url': author.author.url,
                } for author in item.specific.authors.all()],
                'contenttype': item.specific.contenttype,
                'contentsubtype': item.specific.contentsubtype,
                'pdf_download': item.specific.pdf_download,
                'publishing_date': item.specific.publishing_date,
                'title': item.title,
                'topics': [{
                    'id': topic.id,
                    'title': topic.title,
                    'url': topic.url,
                } for topic in item.specific.topics.all()],
                'url': item.url,
            } for item in pages[offset:offsetLimit]
        ]
    }, safe=False)
