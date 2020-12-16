from django.db.models import F
from wagtail.api.v2.filters import (
    FieldsFilter,
    OrderingFilter,
    SearchFilter,
)
from wagtail.api.v2.serializers import PageSerializer
from wagtail.api.v2.views import BaseAPIViewSet

from .models import ArticlePage


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
            article_type__in=[
                ArticlePage.ArticleTypes.INTERVIEW,
                ArticlePage.ArticleTypes.OP_ED,
                ArticlePage.ArticleTypes.OPINION,
            ]
        ).order_by(F('publishing_date').desc(nulls_last=True))
