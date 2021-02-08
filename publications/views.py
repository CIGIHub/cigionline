# from django.db.models import F
# from django.http import JsonResponse
# from wagtail.api.v2.filters import (
#     FieldsFilter,
#     OrderingFilter,
#     SearchFilter,
# )
# from wagtail.api.v2.serializers import PageSerializer
# from wagtail.api.v2.views import BaseAPIViewSet

# from .models import (
#     # PublicationPage,
#     PublicationTypePage,
# )


# def all_publication_types(request):
#     publication_types = PublicationTypePage.objects.public().live().order_by('title')
#     return JsonResponse({
#         'meta': {
#             'total_count': publication_types.count(),
#         },
#         'items': [{
#             'id': publication_type.id,
#             'title': publication_type.title,
#         } for publication_type in publication_types[:50]],
#     }, safe=False)


# class PublicationPageViewSet(BaseAPIViewSet):
#     model = PublicationPage
#     base_serializer_class = PageSerializer
#     filter_backends = [
#         FieldsFilter,
#         OrderingFilter,
#         SearchFilter,
#     ]
#
#     def get_queryset(self):
#         return self.model.objects.public().live().filter(publishing_date__isnull=False).order_by(F('publishing_date').desc(nulls_last=True))
#
#
# class PublicationTypePageViewSet(BaseAPIViewSet):
#     model = PublicationTypePage
#     base_serializer_class = PageSerializer
#     filter_backends = [OrderingFilter]
#
#     def get_queryset(self):
#         return self.model.objects.public().live()
