from django.http import JsonResponse
from django.shortcuts import render
from wagtail.search.models import Query

from .search import cigi_search


def search(request):  # pragma: no cover
    return render(request, 'search/search.html')


def search_api(request):
    searchtext = request.GET.get('searchtext', None)
    if searchtext:
        query = Query.get(searchtext)

        # Record hit
        query.add_hit()

    pages = cigi_search(
        articletypeid=request.GET.get('articletypeid', None),
        authors=request.GET.getlist('author', None),
        content_type=request.GET.get('content_type', None),
        contenttypes=request.GET.getlist('contenttype', None),
        contentsubtypes=request.GET.getlist('contentsubtype', None),
        persontypes=request.GET.getlist('persontype', None),
        projects=request.GET.getlist('project', None),
        publicationtypeid=request.GET.get('publicationtypeid', None),
        searchtext=searchtext,
        sort=request.GET.get('sort', None),
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
            'highlights': page._highlights,
            'id': page.id,
            'title': page.title,
            'url': page.url,
        }
        for field in fields:
            try:
                if field == 'authors':
                    item['authors'] = [{
                        'id': author.author.id,
                        'title': author.author.title,
                        'url': author.author.url,
                    } for author in page.specific.authors.all()]
                elif field == 'cigi_people_mentioned':
                    item['cigi_people_mentioned'] = [{
                        'id': person.value.id,
                        'title': person.value.title,
                        'url': person.value.url,
                    } for person in page.specific.cigi_people_mentioned]
                elif field == 'topics':
                    item['topics'] = [{
                        'id': topic.id,
                        'title': topic.title,
                        'url': topic.url,
                    } for topic in page.specific.topics.all()]
                else:
                    item[field] = getattr(page.specific, field)
            except AttributeError:
                pass
        items.append(item)

    return JsonResponse({
        'meta': {
            'total_count': pages.count(),
        },
        'items': items,
    }, safe=False)
