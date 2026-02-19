from core.models import ArchiveablePageAbstract
from django.http import JsonResponse, HttpResponse

from .models import TopicPage, ThemePage, ProjectPage

from articles.models import ArticlePage
from publications.models import PublicationPage
from multimedia.models import MultimediaPage
from events.models import EventPage

from core.models import ContentPage
from datetime import date
import csv
from urllib.parse import unquote


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


def program_content_within_range(request):
    start_date = date(2024, 8, 1)
    end_date = date(2025, 7, 31)
    themes = ThemePage.objects.live().filter(archive=0).order_by('title')
    results = []

    for theme in themes:
        topic_pages = TopicPage.objects.filter(program_theme=theme)
        theme_content_pages = []

        for topic in topic_pages:
            all_slugs = list(
                topic.content_pages.live().filter(
                    publishing_date__gte=start_date,
                    publishing_date__lte=end_date
                ).values_list('slug', flat=True)
            )
            theme_content_pages += all_slugs

        results.append({
            "name": theme.title,
            "all_content_pages": list(set(theme_content_pages)),
        })

    return JsonResponse({
        "name": "Themes",
        "children": results,
    })


def program_affiliates(request):
    def convert_youtube(url):
        if url and "youtu.be/" in url:
            return url.replace("https://youtu.be/", "https://www.youtube.com/watch?v=")
        return url

    request_type = request.GET.get('type')
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response.write('\ufeff')

    pages_list = []
    authors_list = []
    projects = ProjectPage.objects.live().filter(archive=0).order_by('title')

    for project in projects:
        # include landing page (no video url for project)
        url = unquote(project.url)
        if url.startswith("https://www.cigionline.org"):
            url = url[len("https://www.cigionline.org"):]
        pages_list.append({
            'program': project.title,
            'title': project.title,
            'url': url,
            'pdf': '',
            'video_url': '',
        })

        # pull content pages
        content_pages = project.content_pages.live().all()
        authors = []

        for page in content_pages:
            # normalise page url once
            url = unquote(page.url)
            if url.startswith("https://www.cigionline.org"):
                url = url[len("https://www.cigionline.org"):]

            # try to grab multimedia_url from the specific page
            multimedia_url = getattr(page.specific, 'multimedia_url', '') or ''
            multimedia_url = convert_youtube(unquote(multimedia_url)) if multimedia_url else ''

            if hasattr(page.specific, 'pdf_downloads'):
                for pdf in page.specific.pdf_downloads:
                    pdf_url = unquote(pdf.value['file'].url) if pdf.value['file'] else ''
                    if not pdf_url.startswith("https://www.cigionline.org"):
                        pdf_url = f'https://www.cigionline.org{pdf_url}'
                    pages_list.append({
                        'program': project.title,
                        'title': page.title,
                        'url': url,
                        'pdf': pdf_url,
                        'video_url': multimedia_url,
                    })
            else:
                pages_list.append({
                    'program': project.title,
                    'title': page.title,
                    'url': url,
                    'pdf': '',
                    'video_url': multimedia_url,
                })

            authors += [author for author in getattr(page.specific, 'authors', None).all()]

        for author in list(set(authors)):
            url = unquote(author.author.url) if author.author.url else ''
            if url.startswith("https://www.cigionline.org"):
                url = url[len("https://www.cigionline.org"):]
            authors_list += [{
                'program': project.title,
                'name': author.author.title,
                'url': url,
            }]

    # request experts
    if request_type == 'experts':
        response['Content-Disposition'] = 'attachment; filename="program_experts.csv"'
        writer = csv.writer(response)
        writer.writerow(['Programs', 'Expert', 'URL'])      # CSV header
        for author in authors_list:
            writer.writerow([author['program'], author['name'], author['url']])
        return response

    # default to content page requests
    response['Content-Disposition'] = 'attachment; filename="program_pages.csv"'
    writer = csv.writer(response)
    writer.writerow(['Programs', 'Title', 'Page URL', 'Link URL', 'Video URL'])     # CSV header
    for page in pages_list:
        writer.writerow([
            page['program'],
            page['title'],
            page['url'],
            page['pdf'],
            page['video_url'],
        ])

    return response
