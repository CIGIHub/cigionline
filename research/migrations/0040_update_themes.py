from django.db import migrations
from research.models import TopicPage, ThemePage, ThemeListPage
from wagtail.models import Page


def create_page(page_model, page_title, parent_page_title):
    if not page_model.objects.filter(title=page_title).exists():
        new_page = page_model(title=page_title)
        parent_page = Page.objects.get(title=parent_page_title).specific
        parent_page.add_child(instance=new_page)


def create_theme_list_page(apps, schema_editor):
    if Page.objects.filter(title='Home').exists():
        create_page(
            page_model=ThemeListPage,
            page_title='Themes',
            parent_page_title='Home'
        )


def update_topics(apps, schema_editor):
    themes_topics = {
        'AI and Transformative Technology': [
            'Transformative Technologies',
            'Artificial Intelligence',
            'Quantum Technology',
            'Digital Governance',
        ],
        'Data, Economy, Society': [
            'Competition',
            'Intellectual Property',
            'Data Governance'
            'Digital Economy',
            'Financial Governance',
            'Human Rights',
            'Rights of Society',
        ],
        'Digitalization, Security and Democracy': [
            'Democracy',
            'Gender',
            'Platform Governance',
            'National Security',
            'Space Governance',
            'Cybersecurity',
            'Digital Rights',
            'Foreign Interference',
            'Freedom of Thought',
            'Privacy',
            'Surveillance',
        ],
        'Global Cooperation and Governance': [
            'G20/G7',
            'Trade',
            'Geopolitics',
            'Global Cooperation',
            'Multilateral Institutions',
        ],
    }

    if Page.objects.filter(title='Home').exists():
        for theme_title, topic_titles in themes_topics.items():
            # create theme page
            create_page(
                page_model=ThemePage,
                page_title=theme_title,
                parent_page_title='Themes'
            )
            theme = ThemePage.objects.get(title=theme_title)

            # add theme to topic pages
            for topic_title in topic_titles:
                if TopicPage.objects.filter(title=topic_title).exists():
                    topic = TopicPage.objects.get(title=topic_title)
                    if not topic.program_theme:
                        topic.program_theme = theme
                        topic.save()
                    else:
                        print(f'{topic_title} already has theme - {theme_title}')
                else:
                    print(f'{topic_title} does not exist')


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0039_alter_topic_tags'),
    ]

    operations = [
        migrations.RunPython(create_theme_list_page),
        migrations.RunPython(update_topics),
    ]
