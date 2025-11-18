from wagtail.models import Page
from .models import AnnualReportPage, AnnualReportSlidePage, AnnualReportSPAPage, StrategicPlanSPAPage, StrategicPlanSlidePage
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from wagtail.api.v2.views import PagesAPIViewSet
from utils.helpers import richtext_html, richtext_to_inline_html


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


def get_ordered_slides_annual_report(request, page_id):
    gradient_positions = {
        'left': 'left',
        'right': 'right',
        'top-left': 'left',
        'top-right': 'right',
        'bottom-left': 'left',
        'bottom-right': 'right',
    }
    page = get_object_or_404(Page, id=page_id).specific
    slide_ids = [block.value["slide"].id for block in page.slides]
    year = page.year

    if isinstance(page, AnnualReportSPAPage):
        slides = AnnualReportSlidePage.objects.filter(id__in=slide_ids)
    else:
        slides = []
    slide_map = {slide.id: slide for slide in slides}
    ordered_slides = [slide_map[id] for id in slide_ids if id in slide_map]

    slides = []
    for slide in ordered_slides:
        background_image = slide.background_image.get_rendition('fill-2400x1350').file.url if slide.background_image else ''
        background_image_thumbnail = slide.background_image.get_rendition('fill-384x216').file.url if slide.background_image else ''
        slides.append({
            "id": slide.id,
            "title": slide.title,
            "slug": slide.slug,
            "slide_title": richtext_to_inline_html(slide.slide_title),
            "slide_title_fr": richtext_to_inline_html(slide.slide_title_fr),
            "slide_subtitle": slide.slide_subtitle,
            "slide_content": slide.get_annual_report_slide_content(),
            "slide_type": slide.slide_type,
            "year": year,
            "background_image": background_image,
            "background_image_thumbnail": background_image_thumbnail,
            "background_video": slide.background_video.file.url if slide.background_video else '',
            "background_quote": slide.background_quote,
            "background_quote_font_size": slide.background_quote_font_size,
            "background_quote_fr": slide.background_quote_fr,
            "background_quote_font_size_fr": slide.background_quote_font_size_fr,
            "background_quote_position": slide.background_quote_position,
            "background_gradient_position": gradient_positions.get(slide.background_quote_position, 'left') if slide.background_quote_position else 'left',
            "background_colour": slide.background_colour.replace("_", "-"),
            "include_on_toc": slide.include_on_toc,
            "french_slide": slide.french_slide,
        })

    response_data = {
        "slides": slides
    }

    return JsonResponse(response_data)


def get_ordered_slides_strategic_plan(request, page_id):
    page = get_object_or_404(Page, id=page_id).specific
    slide_ids = [block.value["slide"].id for block in page.slides]

    if isinstance(page, StrategicPlanSPAPage):
        slides = StrategicPlanSlidePage.objects.filter(id__in=slide_ids)
    else:
        slides = []
    slide_map = {slide.id: slide for slide in slides}
    ordered_slides = [slide_map[id] for id in slide_ids if id in slide_map]

    slides = []
    for slide in ordered_slides:
        if slide.background_images:
            background_image = slide.background_images[0].value.get_rendition('fill-1920x1080').file.url
            background_image_thumbnail = slide.background_images[0].value.get_rendition('fill-384x216').file.url
        else:
            if slide.slide_type in ['title', 'toc']:
                background_image = slide.background_image.get_rendition('fill-1920x2160').file.url if slide.background_image else ''
                background_image_thumbnail = slide.background_image.get_rendition('fill-384x432').file.url if slide.background_image else ''
            else:
                background_image = slide.background_image.get_rendition('fill-1920x1080').file.url if slide.background_image else ''
                background_image_thumbnail = slide.background_image.get_rendition('fill-384x216').file.url if slide.background_image else ''
        slides.append({
            "id": slide.id,
            "title": slide.title,
            "slug": slide.slug,
            "slide_title": slide.slide_title,
            "slide_subtitle": slide.slide_subtitle,
            "slide_content": slide.get_strategic_plan_slide_content(),
            "slide_type": slide.slide_type,
            "slide_theme": slide.slide_theme,
            "background_image": background_image,
            "background_images": [
                image.value.get_rendition('fill-1920x1080').file.url for image in slide.background_images
            ],
            "background_image_thumbnail": background_image_thumbnail,
            "background_video": slide.background_video.file.url if slide.background_video else '',
            "background_colour": slide.background_colour.replace("_", "-"),
            "display_vertical_title": slide.display_vertical_title,
            "include_on_toc": slide.include_on_toc,
            "column_size": slide.column_size,
            "alignment": slide.alignment,
        })

    response_data = {
        "slides": slides,
    }

    return JsonResponse(response_data)
