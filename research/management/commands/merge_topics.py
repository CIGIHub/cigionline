from django.core.management.base import BaseCommand
from research.models import TopicPage


class Command(BaseCommand):
    help = 'Merge reserach topics'

    def handle(self, ** options):
        topic_pages = TopicPage.objects.live().all()
        for topic in topic_pages:
            print(topic.id, topic.title)
