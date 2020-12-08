from rest_framework.pagination import PageNumberPagination
from wagtail.api.v2.filters import OrderingFilter
from wagtail.api.v2.serializers import PageSerializer
from wagtail.api.v2.views import BaseAPIViewSet

from .models import MultimediaPage


class MultimediaResultsSetPagination(PageNumberPagination):
    page_size = 18
    max_page_size = 18


class MultimediaPageViewSet(BaseAPIViewSet):
    model = MultimediaPage
    base_serializer_class = PageSerializer
    filter_backends = [
        OrderingFilter,
    ]

    def get_queryset(self):
        return self.model.objects.all().public().live().order_by('-publishing_date')
    # queryset = MultimediaPage.objects.live().order_by('-publishing_date')
    # serializer_class = MultimediaPageSerializer
    # pagination_class = MultimediaResultsSetPagination
