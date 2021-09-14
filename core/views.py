from bs4 import BeautifulSoup
from core.models import ContentPage
from django.http import JsonResponse


def content_pages(request):
    content_pages = ContentPage.objects.live().filter(multimediapage=None).exclude(articlepage__article_type__title__in=['CIGI in the News', 'News Releases']).filter(publishing_date__range=["2020-08-01", "2021-07-31"])

    json_items = []

    for content_page in content_pages:
        authors = ''
        speakers = ''
        event_date = ''
        summary = ''
        if content_page.contenttype == 'Event':
            speakers = content_page.author_names
        else:
            authors = content_page.author_names
            event_date = content_page.publishing_date

        if content_page.contenttype == 'Opinion':
            summary = content_page.specific.short_description
        elif content_page.contenttype == 'Publication':
            for block in content_page.specific.body:
                if block.block_type == 'paragraph':
                    summary += str(block.value)

        soup = BeautifulSoup(summary, features='html5lib')
        summary = soup.get_text()

        json_items.append({
            'id': content_page.id,
            'title': content_page.title,
            'subtitle': content_page.specific.subtitle,
            'authors': [authors] if authors else [],
            'speakers': [speakers] if speakers else [],
            'published_date': content_page.publishing_date,
            'event_date': event_date,
            'url_landing_page': content_page.url,
            'pdf_url': content_page.pdf_download,
            'type': content_page.contenttype.lower(),
            'subtype': [content_page.contentsubtype] if content_page.contentsubtype else [],
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
