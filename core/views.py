from bs4 import BeautifulSoup
from core.models import ContentPage
from django.http import JsonResponse


def ar_timeline_pages(request):
    content_pages = ContentPage.objects.live().filter(projectpage=None, publicationseriespage=None, multimediaseriespage=None, twentiethpagesingleton=None, multimediapage=None, articleseriespage=None).exclude(articlepage__article_type__title__in=['CIGI in the News', 'News Releases', 'Op-Eds']).filter(publishing_date__range=["2020-08-01", "2021-07-31"])

    json_items = []

    for content_page in content_pages:
        type = ''
        subtype = []
        authors = ''
        speakers = ''
        event_date = ''
        summary = ''
        subtitle = content_page.specific.subtitle
        publishing_date = ''
        if content_page.contenttype == 'Event':
            type = 'event'
            speakers = content_page.author_names
            event_date = content_page.publishing_date
        else:
            authors = content_page.author_names
            publishing_date = content_page.publishing_date

        if content_page.contenttype == 'Opinion':
            type = 'article'
            subtype = [content_page.contentsubtype] if content_page.contentsubtype else []
        elif content_page.contenttype == 'Publication':
            type = 'publication'
            subtype = content_page.contentsubtype if content_page.contentsubtype else [],
        try:
            summary = content_page.specific.short_description
        except AttributeError:
            if content_page.specific.subtitle:
                summary = content_page.specific.subtitle
            else:
                for block in content_page.specific.body:
                    if block.block_type == 'paragraph':
                        summary += str(block.value)

        soup = BeautifulSoup(summary, features='html5lib')
        summary = soup.get_text()

        json_items.append({
            'id': str(content_page.id),
            'title': content_page.title,
            'subtitle': subtitle,
            'authors': authors if authors else [],
            'speakers': speakers if speakers else [],
            'published_date': publishing_date,
            'event_date': event_date,
            'url_landing_page': content_page.url,
            'pdf_url': content_page.pdf_download,
            'type': type,
            'subtype': subtype,
            'word_count': content_page.specific.word_count,
            'summary': summary,
            'image': content_page.specific.image_hero.get_rendition('fill-1600x900').url if content_page.specific.image_hero else '',
        })

    return JsonResponse({
        'meta': {
            'total_count': content_pages.count(),
        },
        'items': json_items
    })
