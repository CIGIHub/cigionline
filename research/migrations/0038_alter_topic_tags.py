from django.db import migrations
from research.models import TopicPage
from core.models import ContentPage


def many_to_one(apps, schema_editor):
    # in format of {new_topic_title: [old_topic_titles]}; counterintuitive but useful for verification
    many_to_one_migrations = {
        'Digital Economy': ['Central Banking', 'Digital Currency'],
        'Geopolitics': ['Africa', 'China', 'India'],
        'Multilateral Institutions': ['IMF', 'NAFTA/CUSMA', 'WTO'],
        'Platform Governance': ['Internet Governance'],
        'Transformative Technologies': ['Innovation', 'Innovation Economy'],
    }

    for new_topic_title, old_topic_titles in many_to_one_migrations.items():
        new_topic = TopicPage.objects.get(title=new_topic_title)
        old_topics = [TopicPage.objects.get(title=old_topic_title) for old_topic_title in old_topic_titles]

        # convert to set to dedup
        content_pages = list(set(ContentPage.objects.filter(topics__in=old_topics)))

        print(f'Now processing:{new_topic_title}...')
        print(f'{len(content_pages)} pages were tagged by any of {old_topic_titles}.')

        for page in content_pages:
            for old_topic in old_topics:
                page.topics.remove(old_topic)
            if new_topic not in page.topics.all():
                page.topics.add(new_topic)
            page.save()

        for old_topic in old_topics:
            if old_topic.archive == TopicPage.ArchiveStatus.UNARCHIVED:
                old_topic.archive = TopicPage.ArchiveStatus.ARCHIVED
                old_topic.save()


def one_to_many(apps, schema_editor):
    one_to_many_migrations = {
        'Surveillance & Privacy': ['Privacy', 'Surveillance'],
    }

    for old_topic_title, new_topic_titles in one_to_many_migrations.items():
        old_topic = TopicPage.objects.get(title=old_topic_title)
        new_topics = [TopicPage.objects.get(title=new_topic_title) for new_topic_title in new_topic_titles]
        content_pages = ContentPage.objects.filter(topics__in=[old_topic])
        print(f'Now processing:{old_topic_title}...')
        print(f'{content_pages.count()} pages were tagged with {old_topic_title}.')

        for page in content_pages:
            page.topics.remove(old_topic)
            for new_topic in new_topics:
                if new_topic not in page.topics.all():
                    page.topics.add(new_topic)
            page.save()

        if old_topic.archive == TopicPage.ArchiveStatus.UNARCHIVED:
            old_topic.archive = TopicPage.ArchiveStatus.ARCHIVED
            old_topic.save()


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0037_update_topics'),
    ]

    operations = [
        migrations.RunPython(many_to_one),
        migrations.RunPython(one_to_many),
    ]
