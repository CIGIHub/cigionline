from core.models import ArchiveablePageAbstract
from django.contrib.postgres.lookups import Unaccent
from django.db.models.functions import Lower
from django.http import JsonResponse

from .models import PersonPage


def all_experts(request):
    experts = PersonPage.objects.public().live().filter(
        archive=ArchiveablePageAbstract.ArchiveStatus.UNARCHIVED,
        person_types__name__in=['CIGI Chair', 'Expert'],
    ).order_by(
        Unaccent(Lower('last_name')),
        Unaccent(Lower('first_name')),
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
