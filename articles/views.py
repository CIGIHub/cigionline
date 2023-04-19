from articles.models import ArticleSeriesPage
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


def all_article_series(request):
    article_series = ArticleSeriesPage.objects.live().public().order_by('-publishing_date')

    return JsonResponse(
        {
            'meta': {
                'total_count': article_series.count(),
            },
            'items': [{
                'id': series.id,
                'title': series.title,
                'url': series.url,
                'short_description': series.short_description,
                'image_poster_url': series.image_poster.get_rendition('fill-672x895').url,
                'series_contributors': series.series_contributors,
                'theme': series.theme.name.lower().replace(' ', '-') if series.theme else None,
                'topics': [{
                    'id': topic.id,
                    'title': topic.title,
                    'url': topic.url,
                } for topic in series.topics.all()],

            } for series in article_series]
        },
        safe=False)
