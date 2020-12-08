from rest_framework.serializers import ModelSerializer

from .models import MultimediaPage


class MultimediaPageSerializer(ModelSerializer):
    class Meta:
        model = MultimediaPage
        fields = (
            'id', 'url', 'title', 'publishing_date', 'multimedia_type', 'image_hero_url',
        )
