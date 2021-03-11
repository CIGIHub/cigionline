from django.http import JsonResponse
from .models import AnnualReportPage


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
            'year': annual_report.year,
            'url': annual_report.url,
        } for annual_report in annual_reports]
    })
