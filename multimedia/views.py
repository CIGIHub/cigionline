from wagtail.api.v2.filters import OrderingFilter
from wagtail.api.v2.serializers import PageSerializer
from wagtail.api.v2.views import BaseAPIViewSet

from .models import MultimediaPage


class MultimediaPageViewSet(BaseAPIViewSet):
    model = MultimediaPage
    base_serializer_class = PageSerializer
    filter_backends = [
        OrderingFilter,
    ]

    def get_queryset(self):
        return self.model.objects.public().live().order_by('-publishing_date')
