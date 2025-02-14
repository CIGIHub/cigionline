from django.http import JsonResponse
from .models import AnnualReportPage, AnnualReportSlidePage, AnnualReportSPAPage

from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter


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


api_router = WagtailAPIRouter("wagtailapi")


class AnnualReportSPAPageAPIViewSet(PagesAPIViewSet):
    """Custom API view to expose annual report data."""

    def get_queryset(self):
        return AnnualReportSPAPage.objects.live().public()


class AnnualReportSlidePageAPIViewSet(PagesAPIViewSet):
    """API for fetching slides."""

    def get_queryset(self):
        return AnnualReportSlidePage.objects.live().public()


api_router.register_endpoint("annual_report_spa", AnnualReportSPAPageAPIViewSet)
api_router.register_endpoint("annual_report_slide", AnnualReportSlidePageAPIViewSet)
