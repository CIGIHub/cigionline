from django.forms import ValidationError
import requests
from core.models import ContentPage
from datetime import date
from django.conf import settings
from django.http import HttpResponseBadRequest, JsonResponse
from django.http import HttpResponse
from django.template.response import TemplateResponse
from wagtail.documents.views.multiple import AddView


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


def years(request):
    years = ContentPage.objects.filter(publishing_date__year__isnull=False).values_list('publishing_date__year', flat=True).distinct().order_by('-publishing_date__year')
    return JsonResponse({
        'years': list(years)
    })


class MalwareScannedAddview(AddView):
    def scan_file_for_viruses(self, file):
        api_key = settings.VIRUSTOTAL_API_KEY
        url = 'https://www.virustotal.com/api/v3/files'
        headers = {
            'x-apikey': api_key
        }
        files = {
            'file': file
        }
        response = requests.post(url, headers=headers, files=files)
        print(response)

        if response.status_code != 200:
            raise ValidationError('Failed to scan file for viruses')

        result = response.json()
        print(result)
        if result.get('data', {}).get('attributes', {}).get('last_analysis_stats', {}).get('malicious', 0) > 0:
            raise ValidationError('The uploaded file is infected with malware.')

    def post(self, request):
        if not request.FILES:
            return HttpResponseBadRequest("Must upload a file")

        # Perform the malware check on the file
        try:
            for file in request.FILES.getlist('files[]'):
                self.scan_file_for_viruses(file)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

        # Build a form for validation
        upload_form_class = self.get_upload_form_class()
        form = upload_form_class(
            {
                "title": request.POST.get("title", request.FILES["files[]"].name),
                "collection": request.POST.get("collection"),
            },
            {
                "file": request.FILES["files[]"],
            },
            user=request.user,
        )

        if form.is_valid():
            # Save it
            self.object = self.save_object(form)

            # Success! Send back an edit form for this object to the user
            return JsonResponse(self.get_edit_object_response_data())
        elif "file" in form.errors:
            # The uploaded file is invalid; reject it now
            return JsonResponse(self.get_invalid_response_data(form))
        else:
            # Some other field of the form has failed validation, e.g. a required metadata field
            # on a custom image model. Store the object as an upload_model instance instead and
            # present the edit form so that it will become a proper object when successfully filled in
            self.upload_object = self.upload_model.objects.create(
                file=self.request.FILES["files[]"], uploaded_by_user=self.request.user
            )
            self.object = self.model(
                title=self.request.FILES["files[]"].name,
                collection_id=self.request.POST.get("collection"),
            )

            return JsonResponse(self.get_edit_upload_response_data())
