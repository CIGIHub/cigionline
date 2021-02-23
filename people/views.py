from django.http import JsonResponse

from .search import expert_latest_activity_search, experts_search


def all_experts(request):
    experts = experts_search(
        searchtext=request.GET.get('search', None),
        topics=request.GET.getlist('topic', None),
    )

    items = []
    for expert in experts[:150]:
        item = {
            'expertise': expert.expertise_list,
            'id': expert.id,
            'image_square_url': expert.image_square_url,
            'latest_activity': None,
            'position': expert.position,
            'title': expert.title,
            'url': expert.url,
        }
        latest_activity = expert_latest_activity_search(expert_id=expert.id)
        for activity in latest_activity[:1]:
            item['latest_activity'] = {
                'contentsubtype': activity.contentsubtype,
                'contenttype': activity.contenttype,
                'id': activity.id,
                'title': activity.title,
                'url': activity.url,
            }
        items.append(item)
    return JsonResponse({
        'meta': {
            'total_count': experts.count(),
        },
        'items': items,
    }, safe=False)
