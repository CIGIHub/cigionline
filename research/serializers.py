from rest_framework.serializers import ModelSerializer

from .models import TopicPage


class TopicPageSerializer(ModelSerializer):
    class Meta:
        model = TopicPage
        fields = [
            'id',
            'url',
            'title',
        ]
