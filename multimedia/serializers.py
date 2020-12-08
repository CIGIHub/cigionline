from research.serializers import TopicPageSerializer
from rest_framework.serializers import ModelSerializer

from .models import MultimediaPage


class MultimediaPageSerializer(ModelSerializer):
    topics = TopicPageSerializer(many=True)

    class Meta:
        model = MultimediaPage
        fields = [
            'id',
            'url',
            'title',
            'publishing_date',
            'multimedia_type',
            'image_hero_url',
            'topics',
        ]
