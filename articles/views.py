from django.db.models import F
from wagtail.api.v2.filters import (
    FieldsFilter,
    OrderingFilter,
    SearchFilter,
)
from wagtail.api.v2.serializers import PageSerializer
from wagtail.api.v2.views import BaseAPIViewSet

from .models import (
    ArticlePage,
    ArticleSeriesPage,
    ArticleTypePage,
)


class ArticleSeriesPageViewSet(BaseAPIViewSet):
    model = ArticleSeriesPage
    base_serializer_class = PageSerializer

    def get_queryset(self):
        return self.model.objects.public().live().filter(publishing_date__isnull=False).order_by(F('publishing_date').desc(nulls_last=True))


class MediaPageViewSet(BaseAPIViewSet):
    model = ArticlePage
    base_serializer_class = PageSerializer
    filter_backends = [
        FieldsFilter,
        OrderingFilter,
        SearchFilter,
    ]

    def get_queryset(self):
        return self.model.objects.public().live().filter(
            article_type__title__in=[
                'CIGI in the News',
                'News Releases',
                'Op-Eds',
            ],
            publishing_date__isnull=False
        ).order_by(F('publishing_date').desc(nulls_last=True))


class OpinionPageViewSet(BaseAPIViewSet):
    model = ArticlePage
    base_serializer_class = PageSerializer
    filter_backends = [
        FieldsFilter,
        OrderingFilter,
        SearchFilter,
    ]

    def get_queryset(self):
        return self.model.objects.public().live().filter(
            article_type__title__in=[
                'Interviews',
                'Op-Eds',
                'Opinion',
            ],
            publishing_date__isnull=False
        ).order_by(F('publishing_date').desc(nulls_last=True))


class ArticlePageViewSet(BaseAPIViewSet):
    model = ArticlePage
    base_serializer_class = PageSerializer
    filter_backends = [
        FieldsFilter,
        OrderingFilter,
        SearchFilter,
    ]

    def get_queryset(self):
        return self.model.objects.public().live().filter(publishing_date__isnull=False).order_by(F('publishing_date').desc(nulls_last=True))


class ArticleTypePageViewSet(BaseAPIViewSet):
    model = ArticleTypePage
    base_serializer_class = PageSerializer
    filter_backends = [OrderingFilter]

    def get_queryset(self):
        return self.model.objects.public().live()
