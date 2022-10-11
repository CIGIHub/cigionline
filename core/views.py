from core.models import ContentPage
from datetime import date
from django.http import JsonResponse
from django.http import HttpResponse
from django.template.response import TemplateResponse


def ar_timeline_pages(request):
    if request.user.is_authenticated:
        year = int(request.GET.get('year')) if request.GET.get('year') else date.today().year
        content_pages = ContentPage.objects.live().filter(projectpage=None, publicationseriespage=None, multimediaseriespage=None, twentiethpagesingleton=None, multimediapage=None, articleseriespage=None).exclude(articlepage__article_type__title__in=['CIGI in the News', 'News Releases', 'Op-Eds']).filter(publishing_date__range=[f'{year - 1}-08-01', f'{year}-07-31'])

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
            image = ''
            if content_page.contenttype == 'Event':
                type = 'event'
                speakers = content_page.author_names
                event_date = content_page.publishing_date
                image = content_page.specific.image_hero.get_rendition('fill-1600x900').url if content_page.specific.image_hero else ''
            else:
                authors = content_page.author_names
                publishing_date = content_page.publishing_date

            if content_page.contenttype == 'Opinion':
                type = 'article'
                subtype = [content_page.contentsubtype] if content_page.contentsubtype else []
                image = content_page.specific.image_hero.get_rendition('fill-1600x900').url if content_page.specific.image_hero else ''
            if content_page.contenttype == 'Publication':
                type = 'publication'
                subtype = [content_page.contentsubtype] if content_page.contentsubtype else []
                image = content_page.specific.image_feature.get_rendition('fill-1600x900').url if content_page.specific.image_feature else ''
            try:
                summary = content_page.specific.short_description
            except AttributeError:
                summary = ''
                if content_page.specific.subtitle:
                    summary = content_page.specific.subtitle
                else:
                    for block in content_page.specific.body:
                        if block.block_type == 'paragraph':
                            summary += str(block.value)

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
                'image': image,
            })

        return JsonResponse({
            'meta': {
                'total_count': content_pages.count(),
            },
            'items': json_items
        })
    return HttpResponse('Unauthorized', status=401)


def old_images(request):
    if request.user.is_authenticated:
        content_pages = ContentPage.objects.filter(articlepage__isnull=False).filter(publishing_date__lt='2017-01-01')
        pages = []
        for content_page in content_pages:
            if content_page.specific.image_hero:
                pages.append({
                    'id': content_page.id,
                    'url': content_page.url,
                    'title': content_page.title,
                    'publishing_date': content_page.publishing_date,
                    'image_hero_url_1600_900': content_page.specific.image_hero.get_rendition('fill-1600x900').url if content_page.specific.image_hero else '',
                    'image_hero_url_width_1760': content_page.specific.image_hero.get_rendition('width-1760').url if content_page.specific.image_hero else '',
                    'image_feature_url': content_page.specific.image_feature.get_rendition('fill-1600x900').url if content_page.specific.image_feature else '',
                })
        pages.sort(key=lambda x: x['publishing_date'], reverse=True)
        return TemplateResponse(request, 'core/old_pages_list.html', {'pages': pages, 'count': len(pages)})
    return HttpResponse('Unauthorized', status=401)
