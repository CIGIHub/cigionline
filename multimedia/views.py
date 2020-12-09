from wagtail.api.v2.filters import FieldsFilter, OrderingFilter, SearchFilter
from wagtail.api.v2.serializers import PageSerializer
from wagtail.api.v2.views import BaseAPIViewSet

from .models import MultimediaPage


class MultimediaPageViewSet(BaseAPIViewSet):
    model = MultimediaPage
    base_serializer_class = PageSerializer
    filter_backends = [
        FieldsFilter,
        OrderingFilter,
        SearchFilter,
    ]

    def get_queryset(self):
        return self.model.objects.all().public().live().order_by('-publishing_date')
