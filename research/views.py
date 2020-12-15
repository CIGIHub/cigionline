from core.models import ArchiveablePageAbstract
from wagtail.api.v2.filters import (
    OrderingFilter,
)
from wagtail.api.v2.serializers import PageSerializer
from wagtail.api.v2.views import BaseAPIViewSet

from .models import TopicPage


class TopicPageViewSet(BaseAPIViewSet):
    model = TopicPage
    base_serializer_class = PageSerializer
    filter_backends = [OrderingFilter]

    def get_queryset(self):
        return self.model.objects.public().live().filter(archive=ArchiveablePageAbstract.ArchiveStatus.UNARCHIVED).order_by('title')
