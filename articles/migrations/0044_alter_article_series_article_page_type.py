from django.db import migrations
from articles.models import ArticleSeriesPage, ArticleTypePage
from wagtail.models import Page


def update_article_pages(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0043_opinionseriespage_image_banner'),
    ]

    operations = [
        migrations.RunPython(update_article_pages),
    ]
