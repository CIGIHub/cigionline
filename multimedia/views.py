from rest_framework.mixins import ListModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet

from .models import MultimediaPage
from .serializers import MultimediaPageSerializer


class MultimediaResultsSetPagination(PageNumberPagination):
    page_size = 18
    max_page_size = 18


class MultimediaPageViewSet(GenericViewSet, ListModelMixin):
    queryset = MultimediaPage.objects.live().order_by('-publishing_date')
    serializer_class = MultimediaPageSerializer
    pagination_class = MultimediaResultsSetPagination
