from django.db.models import F
from wagtail.api.v2.filters import (
    FieldsFilter,
    OrderingFilter,
    SearchFilter,
)
from wagtail.api.v2.serializers import PageSerializer
from wagtail.api.v2.views import BaseAPIViewSet

from .models import (
    PublicationPage,
    PublicationTypePage,
)


class PublicationPageViewSet(BaseAPIViewSet):
    model = PublicationPage
    base_serializer_class = PageSerializer
    filter_backends = [
        FieldsFilter,
        OrderingFilter,
        SearchFilter,
    ]

    def get_queryset(self):
        return self.model.objects.public().live().filter(publishing_date__isnull=False).order_by(F('publishing_date').desc(nulls_last=True))


class PublicationTypePageViewSet(BaseAPIViewSet):
    model = PublicationTypePage
    base_serializer_class = PageSerializer
    filter_backends = [OrderingFilter]

    def get_queryset(self):
        return self.model.objects.public().live()
