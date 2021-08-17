from core.models import ArchiveablePageAbstract
from django.contrib.postgres.lookups import Unaccent
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.core.cache import cache

from .models import PeoplePage, PersonPage
from .search import experts_search
from .search_expert import expert_latest_activity_search

EXPERTS_API_CACHE_TIMEOUT = 86400


def all_experts(request):

    searchtext = request.GET.get('search', None)
    sort = request.GET.get('sort', None)
    topics = request.GET.getlist('topic', None)

    # Check if query exists in cache
    cache_key = "all_experts"
    if searchtext:
        cache_key += f"_{searchtext}"
    if sort:
        cache_key += f"_{sort}"
    if topics:
        cache_key += f"_{topics}"

    response = cache.get(cache_key)

    if response:
        return JsonResponse(response, safe=False)
    else:

        experts = experts_search(
            searchtext=searchtext,
            sort=sort,
            topics=topics,
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
                'url': expert.get_url(request),
            }
            latest_activity = expert_latest_activity_search(expert_id=expert.id)
            for activity in latest_activity[:1]:
                item['latest_activity'] = {
                    'contentsubtype': activity.contentsubtype,
                    'contenttype': activity.contenttype,
                    'id': activity.id,
                    'title': activity.title,
                    'url': activity.get_url(request),
                }
            items.append(item)

        response = {
            'meta': {
                'total_count': experts.count(),
            },
            'items': items,
        }

        # Set the cache with a timeout of 1 day
        cache.set(cache_key, response, timeout=EXPERTS_API_CACHE_TIMEOUT)

        return JsonResponse(response, safe=False)


def all_staff(request):
    staff = PersonPage.objects.live().filter(
        archive=ArchiveablePageAbstract.ArchiveStatus.UNARCHIVED,
        person_types__name='Staff'
    ).order_by(Unaccent(Lower('last_name')), Unaccent(Lower('first_name')))

    return JsonResponse({
        'meta': {
            'total_count': staff.count(),
        },
        'items': [{
            'email': person.email,
            'id': person.id,
            'last_name': person.last_name,
            'phone_number': person.phone_number_clean,
            'position': person.position,
            'title': person.title,
            'url': person.get_url(request),
        } for person in staff[:50]]
    })

def all_experts_search(request):
    experts = PersonPage.objects.public().live().filter(archive=ArchiveablePageAbstract.ArchiveStatus.UNARCHIVED, person_types__name__in=['Expert', 'CIGI Chair']).order_by('title')
    return JsonResponse({
        'meta': {
            'total_count': experts.count(),
        },
        'items': [{
            'id': expert.id,
            'title': expert.title,
        } for expert in experts],
    }, safe=False)
