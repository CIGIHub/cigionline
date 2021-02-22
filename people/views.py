from django.http import JsonResponse

from .search import experts_search


def all_experts(request):
    experts = experts_search(
        searchtext=request.GET.get('search', None),
        topics=request.GET.getlist('topic', None),
    )

    return JsonResponse({
        'meta': {
            'total_count': experts.count(),
        },
        'items': [{
            'id': expert.id,
            'title': expert.title,
            'url': expert.url,
        } for expert in experts[:150]],
    }, safe=False)
