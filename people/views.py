from core.models import ArchiveablePageAbstract
from django.contrib.postgres.lookups import Unaccent
from django.db.models.functions import Lower
from wagtail.api.v2.filters import (
    FieldsFilter,
    OrderingFilter,
    SearchFilter,
)
from wagtail.api.v2.serializers import PageSerializer
from wagtail.api.v2.views import BaseAPIViewSet

from .models import (
    PersonPage,
)


class ExpertPageViewSet(BaseAPIViewSet):
    model = PersonPage
    base_serializer_class = PageSerializer
    filter_backends = [
        FieldsFilter,
        OrderingFilter,
        SearchFilter,
    ]

    def get_queryset(self):
        return self.model.objects.public().live().filter(
            archive=ArchiveablePageAbstract.ArchiveStatus.UNARCHIVED,
            person_types__name__in=['CIGI Chair', 'Expert']
        ).order_by(Unaccent(Lower('last_name')), Unaccent(Lower('first_name')))
