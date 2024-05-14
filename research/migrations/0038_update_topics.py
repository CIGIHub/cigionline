from django.db import migrations
from research.models import TopicPage
from wagtail.models import Page


def rename_topics(apps, schema_editor):
    to_rename = {
        'Big Data': 'Data Governance',
        'Emerging Technology': 'Transformative Technologies',
        'Financial Systems': 'Financial Governance',
        'Security': 'National Security',
        'Space': 'Space Governance',
    }

    for old_title, new_title in to_rename.items():
        if TopicPage.objects.filter(title=old_title).exists() and not TopicPage.objects.filter(title=new_title).exists():
            topic = TopicPage.objects.get(title=old_title)
            topic.title = new_title
            topic.save()


def create_topics(apps, schema_editor):
    new_topics = [
        'Cybersecurity',
        'Digital Economy',
        'Digital Rights',
        'Digital Governance',
        'Foreign Interference',
        'Freedom of Thought',
        'Geopolitics',
        'Global Cooperation',
        'Human Rights',  # This topic already exists; unarchive it
        'Multilateral Institutions',
        'Privacy',
        'Quantum Technology',
        'Rights of Society',
        'Surveillance',
    ]

    for title in new_topics:
        if not TopicPage.objects.filter(title=title).exists():
            if Page.objects.filter(title='Topics').exists():
                parent_page = Page.objects.get(title='Topics').specific
                new_page = TopicPage(title=title)
                parent_page.add_child(instance=new_page)
        else:  # Unarchive existing topics
            topic = TopicPage.objects.get(title=title)
            if topic.archive == TopicPage.ArchiveStatus.ARCHIVED:
                topic.archive = TopicPage.ArchiveStatus.UNARCHIVED
                topic.save()


def archive_topics(apps, schema_editor):
    to_archive = [
        'Future of Work',
        'Standards',
        'Systemic Risk',
    ]

    for title in to_archive:
        if TopicPage.objects.filter(title=title).exists():
            topic = TopicPage.objects.get(title=title)

            if topic.archive == TopicPage.ArchiveStatus.UNARCHIVED:
                topic.archive = TopicPage.ArchiveStatus.ARCHIVED
                topic.save()


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0037_auto_20240508_1546'),
    ]

    operations = [
        migrations.RunPython(rename_topics),
        migrations.RunPython(create_topics),
        migrations.RunPython(archive_topics),
    ]
