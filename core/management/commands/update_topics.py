from django.core.management.base import BaseCommand
from articles.models import ArticleSeriesPage
from research.models import TopicPage
from ...models import ContentPage


class Command(BaseCommand):
    def handle(self, *args, **options):
        # article_pages = ContentPage.objects.filter(topics__title="Central Banking")
        # topic_to_add = TopicPage.objects.get(title="Financial Systems")
        # topic_to_remove = TopicPage.objects.get(title="Central Banking")

        # for page in article_pages:
        #     page.topics.remove(topic_to_remove)
        #     if topic_to_add not in page.topics.all():
        #         page.topics.add(topic_to_add)
        #     page.save()

        page = ContentPage.objects.specific.filter(topics__title="IMF", archive=True)
        print(page)