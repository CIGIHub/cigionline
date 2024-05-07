from django.db import migrations
from research.models import TopicPage
from wagtail.models import Page


def rename_topics(apps, schema_editor):
    to_rename = {
        'Emerging Technology': 'Transformative Technologies',
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
        'Data Governance',
        'Digital Economy',
        'Digital Governance',
        'Digital Rights',
        'Financial Governance',
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


def migrate_topics(apps, schema_editor):
    many_to_one_migrations = {
        'Big Data': 'Data Governance',
        'Central Banking': 'Digital Economy',
        'Digital Currency': 'Digital Economy',
        'Financial Systems': 'Financial Governance',
        'Africa': 'Geopolitics',
        'China': 'Geopolitics',
        'India': 'Geopolitics',
        'IMF': 'Multilateral Institutions',
        'NAFTA/CUSMA': 'Multilateral Institutions',
        'WTO': 'Multilateral Institutions',
        'Internet Governance': 'Platform Governance',
        'Innovation': 'Transformative Technologies',
        'Innovation Economy': 'Transformative Technologies',
    }

    one_to_many_migrations = [
        {'Surveillance & Privacy': ['Privacy', 'Surveillance']},
    ]


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0036_alter_projectpage_body'),
    ]

    operations = [
        migrations.RunPython(rename_topics),
        migrations.RunPython(create_topics),
        migrations.RunPython(archive_topics),
        # migrations.RunPython(migrate_topics),
    ]
