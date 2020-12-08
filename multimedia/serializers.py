from rest_framework.serializers import ModelSerializer

from .models import MultimediaPage


class MultimediaPageSerializer(ModelSerializer):
    class Meta:
        model = MultimediaPage
        fields = (
            'id', 'title', 'publishing_date', 'multimedia_type',
        )
