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
            'expertise': expert.expertise_list,
            'id': expert.id,
            'image_square_url': expert.image_square_url,
            'position': expert.position,
            'title': expert.title,
            'url': expert.url,
        } for expert in experts[:150]],
    }, safe=False)
