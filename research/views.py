from core.models import ArchiveablePageAbstract
from django.http import JsonResponse

from .models import TopicPage, ThemePage, ProjectPage

from articles.models import ArticlePage
from publications.models import PublicationPage
from multimedia.models import MultimediaPage
from events.models import EventPage

from core.models import ContentPage


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


def topic_contentpages(request):
    topics = TopicPage.objects.live().filter(archive=0).order_by('title')
    results = []

    for topic in topics:
        results.append({
            "name": topic.title,
            "content_pages": topic.content_pages.count(),
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
        })

    return JsonResponse({
        "name": "Topics",
        "children": results,
    })


def overlapping_topics_verification(request):
    topics = {
        'Digital Economy': ['Central Banking', 'Digital Currency'],
        'Geopolitics': ['Africa', 'China', 'India'],
        'Multilateral Institutions': ['IMF', 'NAFTA/CUSMA', 'WTO'],
        'Platform Governance': ['Platform Governance', 'Internet Governance'],
        'Transformative Technologies': ['Emerging Technology', 'Innovation', 'Innovation Economy'],
    }

    results = []

    for new_topic_title, old_topic_titles in topics.items():
        old_topics = []
        no_longer_exists = []

        for old_topic_title in old_topic_titles:
            if TopicPage.objects.filter(title=old_topic_title).exists():
                old_topics.append(TopicPage.objects.get(title=old_topic_title))
            else:
                no_longer_exists.append(old_topic_title)

        content_pages = list(set(ContentPage.objects.filter(topics__in=old_topics)))

        results.append({
            "new_topic": new_topic_title,
            "targeted_old_topics": ', '.join(old_topic_titles),
            "topic_no_longer_exists": ', '.join(no_longer_exists),
            "content_pages": len(content_pages),
        })

    return JsonResponse({
        "name": "Overlapping Topics",
        "children": results,
    })


def themes(request):
    themes = ThemePage.objects.live().filter(archive=0).order_by('title')
    results = []

    for theme in themes:
        topic_pages = TopicPage.objects.filter(program_theme=theme)
        content_pages = []

        for topic in topic_pages:
            content_pages += topic.content_pages.all()

        results.append({
            "name": theme.title,
            "content_pages": len(list(set(content_pages))),
        })

    return JsonResponse({
        "name": "Themes",
        "children": results,
    })


def programs(request):
    themes = ThemePage.objects.live().filter(archive=0).order_by('title')
    theme_results = []

    for theme in themes:
        topic_pages = TopicPage.objects.filter(program_theme=theme)
        topic_results = []

        for topic in topic_pages:
            program_pages = ProjectPage.objects.filter(topics__in=[topic])
            program_results = []

            for program in program_pages:
                program_results.append({
                    "name": program.title,
                    "value": program.content_pages.count(),
                })

            topic_results.append({
                "name": topic.title,
                "children": program_results,
            })

        theme_results.append({
            "name": theme.title,
            "children": topic_results,
        })

    return JsonResponse({
        "name": "Themes",
        "children": theme_results,
    })
