from django.db import migrations
from research.models import TopicPage
from wagtail.models import Page


def migrate_topics(apps, schema_editor):
    many_to_one_migrations = {
        'Central Banking': 'Digital Economy',
        'Digital Currency': 'Digital Economy',
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
        ('research', '0037_update_topics'),
    ]

    operations = [
        migrations.RunPython(migrate_topics),
    ]
