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
