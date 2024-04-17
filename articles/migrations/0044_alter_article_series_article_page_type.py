from django.db import migrations
from articles.models import ArticleSeriesPage, ArticleTypePage


def update_article_pages(apps, schema_editor):
    series_pages = ArticleSeriesPage.objects.all()
    essay_type = ArticleTypePage.objects.get(title='Essay')

    for series_page in series_pages:
        for series_item in series_page.series_items.all():
            page = series_item.content_page.specific
            if page.__class__.__name__ == 'ArticlePage':
                page.article_type = essay_type
                page.save()


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0043_opinionseriespage_image_banner'),
    ]

    operations = [
        migrations.RunPython(update_article_pages),
    ]
