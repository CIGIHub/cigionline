from .models import AnnualReportPage, AnnualReportSlidePage, AnnualReportSPAPage
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from wagtail.api.v2.views import PagesAPIViewSet


def all_annual_reports(request):
    annual_reports = AnnualReportPage.objects.live().order_by('-year')

    return JsonResponse({
        'meta': {
            'total_count': annual_reports.count(),
        },
        'items': [{
            'report_english': annual_report.report_english.file.url if annual_report.report_english else '',
            'report_french': annual_report.report_french.file.url if annual_report.report_french else '',
            'report_financial': annual_report.report_financial.file.url if annual_report.report_financial else '',
            'report_interactive': annual_report.report_interactive,
            'title': annual_report.title,
            'url': annual_report.url,
            'year': annual_report.year,
        } for annual_report in annual_reports]
    })


class AnnualReportSPAPageAPIViewSet(PagesAPIViewSet):
    """Custom API view to expose annual report data."""

    def get_queryset(self):
        return AnnualReportSPAPage.objects.live().public()


class AnnualReportSlidePageAPIViewSet(PagesAPIViewSet):
    """API for fetching slides."""

    def get_queryset(self):
        return AnnualReportSlidePage.objects.live().public()


def get_ordered_slides(request, page_id):
    page = get_object_or_404(AnnualReportSPAPage, id=page_id)
    slide_ids = [block.value["slide"].id for block in page.slides]
    slides = AnnualReportSlidePage.objects.filter(id__in=slide_ids)
    slide_map = {slide.id: slide for slide in slides}
    ordered_slides = [slide_map[id] for id in slide_ids if id in slide_map]

    response_data = {
        "slides": [
            {
                "id": slide.id,
                "title": slide.title,
                "slug": slide.slug,
                "slide_title": slide.slide_title,
                "slide_content": slide.slide_content,
                "slide_type": slide.slide_type,
                "background_image": slide.background_image.get_rendition('original').file.url if slide.background_image else '',
                "background_video": slide.background_video.file.url if slide.background_video else '',
                "include_on_toc": slide.include_on_toc,
            }
            for slide in ordered_slides
        ]
    }
    print(response_data)

    return JsonResponse(response_data)
