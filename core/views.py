from core.models import ContentPage
from django.http import JsonResponse
from django.template.response import TemplateResponse
from datetime import datetime


def old_images(request):
    content_pages = ContentPage.objects.filter(articlepage__isnull=False).filter(publishing_date__lt='2017-01-01')
    pages = []
    for content_page in content_pages:
        if content_page.specific.image_hero:
            pages.append({
                'title': content_page.title,
                'publishing_date': content_page.publishing_date,
                'image_hero_url': content_page.specific.image_hero.get_rendition('fill-1600x900').url if content_page.specific.image_hero else '',
                'image_feature_url': content_page.specific.image_feature.get_rendition('fill-1600x900').url if content_page.specific.image_feature else '',
            })
    pages.sort(key=lambda x: x['publishing_date'], reverse=True)
    return TemplateResponse(request, 'core/old_pages_list.html', {'pages': pages, 'count': len(pages)})
