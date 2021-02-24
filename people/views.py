from core.models import ArchiveablePageAbstract
from django.contrib.postgres.lookups import Unaccent
from django.db.models.functions import Lower
from django.http import JsonResponse

from .models import PersonPage
from .search import expert_latest_activity_search, experts_search


def all_experts(request):
    experts = experts_search(
        searchtext=request.GET.get('search', None),
        sort=request.GET.get('sort', None),
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
    return JsonResponse({
        'meta': {
            'total_count': experts.count(),
        },
        'items': items,
    }, safe=False)


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
