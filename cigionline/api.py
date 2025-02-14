from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter
from annual_reports.views import AnnualReportSlidePageAPIViewSet, AnnualReportSPAPageAPIViewSet

api_router = WagtailAPIRouter('wagtailapi')
api_router.register_endpoint("annual_report", AnnualReportSPAPageAPIViewSet)
api_router.register_endpoint("annual_report_slide", AnnualReportSlidePageAPIViewSet)
