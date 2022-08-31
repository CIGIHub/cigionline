from django.core.management.base import BaseCommand
from articles.models import ArticleSeriesPage
from research.models import TopicPage
from ...models import ContentPage


class Command(BaseCommand):
    def handle(self, *args, **options):
        topics_to_merge = [
            ['Central Banking', 'Financial Systems'],
            ['IMF', 'Financial Systems'],
            ['NAFTA/CUSMA', 'Trade'],
            ['WTO', 'Trade'],
        ]

        for topics in topics_to_merge:
            article_pages = ContentPage.objects.filter(topics__title=topics[0])
            print(f'Found {len(article_pages)} pages for topic {topics[0]}')
            topic_to_add = TopicPage.objects.get(title=topics[1])
            topic_to_remove = TopicPage.objects.get(title=topics[0])

            for page in article_pages:
                try:
                    print(f'Removing {topic_to_remove} from {page}')
                    page.topics.remove(topic_to_remove)
                except Exception:
                    print('error removing topic')
                    break

                try:
                    print(f'Adding {topic_to_add} to {page}')
                    if topic_to_add not in page.topics.all():
                        page.topics.add(topic_to_add)
                    page.save()
                except Exception:
                    print('error adding topic')
                    break
