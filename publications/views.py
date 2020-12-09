from wagtail.api.v2.filters import OrderingFilter
from wagtail.api.v2.serializers import PageSerializer
from wagtail.api.v2.views import BaseAPIViewSet

from .models import PublicationPage


class PublicationPageViewSet(BaseAPIViewSet):
    model = PublicationPage
    base_serializer_class = PageSerializer
    filter_backends = [
        OrderingFilter,
    ]

    def get_queryset(self):
        return self.model.objects.public().live().order_by('-publishing_date')
