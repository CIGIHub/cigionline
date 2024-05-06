from core.models import ArchiveablePageAbstract
from django.http import JsonResponse

from .models import TopicPage
from articles.models import ArticlePage
from publications.models import PublicationPage
from multimedia.models import MultimediaPage
from events.models import EventPage


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


def topic_items(request):
    topics = TopicPage.objects.live().filter(archive=0).order_by('title')
    results = []

    for topic in topics:
        results.append({
            "name": topic.title,
            "children": [
                {
                    "name": "Articles",
                    "value": ArticlePage.objects.filter(topics__in=[topic.id]).count(),
                },
                {
                    "name": "Publications",
                    "value": PublicationPage.objects.filter(topics__in=[topic.id]).count(),
                },
                {
                    "name": "Multimedia",
                    "value": MultimediaPage.objects.filter(topics__in=[topic.id]).count(),
                },
                {
                    "name": "Events",
                    "value": EventPage.objects.filter(topics__in=[topic.id]).count(),
                },
            ],
            "content_pages": topic.content_pages.count(),
        })

    return JsonResponse({
        "name": "Topics",
        "children": results,
    })
