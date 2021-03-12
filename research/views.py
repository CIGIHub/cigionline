from core.models import ArchiveablePageAbstract
from django.http import JsonResponse

from .models import TopicPage


def all_topics(request):
    topics = TopicPage.objects.public().live().filter(archive=ArchiveablePageAbstract.ArchiveStatus.UNARCHIVED).order_by('title')
    return JsonResponse({
        'meta': {
            'total_count': topics.count(),
        },
        'items': [{
            'id': topic.id,
            'title': topic.title,
            'url': topic.get_url(request),
        } for topic in topics[:100]],
    }, safe=False)
