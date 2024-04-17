from articles.models import ArticleSeriesPage, ArticleTypePage
from django.http import JsonResponse


def ai_ethics(request):
    series_page = ArticleSeriesPage.objects.get(slug='the-ethics-of-automated-warfare-and-artificial-intelligence')
    introduction_page = series_page.series_items.first().content_page.specific

    return JsonResponse({
        'title': introduction_page.title,
        'date': introduction_page.publishing_date.strftime('%B %-d, %Y'),
        'authors': [{
                    'title': author.author.title,
                    'url': author.author.url,
                    } for author in introduction_page.specific.authors.all()],
        'image': introduction_page.specific.image_hero.get_rendition('width-1000').url,
        'body': str(introduction_page.body),
    })


def get_article_series_article_pages(request):
    series_pages = ArticleSeriesPage.objects.all()
    article_pages = []
    series_summary = [{'total_series_count': len(series_pages)}]

    for series_page in series_pages:
        series_articles = []
        for series_item in series_page.series_items.all():
            page = series_item.content_page.specific
            if page.__class__.__name__ == 'ArticlePage':
                series_articles.append({
                    'title': page.title,
                    'date': page.publishing_date.strftime('%B %-d, %Y'),
                    'authors': [{
                        'title': author.author.title,
                        'url': author.author.url,
                    } for author in page.specific.authors.all()],
                    'page_type': page.__class__.__name__,
                    'page_subtype': page.article_type.title,
                    'series': series_page.title,
                    'series_date': series_page.publishing_date.strftime('%B %-d, %Y'),
                })
        article_pages += series_articles
        series_summary.append({
            'series_title': series_page.title,
            'date': series_page.publishing_date.strftime('%B %-d, %Y'),
            'articles_count': len(series_articles),
            'opinion_count': len([article for article in series_articles if article['page_subtype'] == 'Opinion']),
            'essay_count': len([article for article in series_articles if article['page_subtype'] == 'Essay']),
        })

    return JsonResponse({'summary': series_summary, 'articles': article_pages})
