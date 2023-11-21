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


def opinion_pages(request):
    from datetime import datetime
    from articles.models import ArticlePage

    start_date = datetime.strptime('2023-06-01', '%Y-%m-%d').date()
    end_date = datetime.strptime('2023-11-21', '%Y-%m-%d').date()

    opinions = ArticlePage.objects.filter(
        publishing_date__range=(start_date, end_date),
        article_type=118,
    )

    op_eds = ArticlePage.objects.filter(
        publishing_date__range=(start_date, end_date),
        article_type=116,
    )

    # for verification purposes
    # opinion_list = []
    # for opinion in opinions:
    #     opinion_list.append({
    #         'title': opinion.title,
    #         'date': opinion.publishing_date.strftime('%B %-d, %Y'),
    #         'authors': [{
    #             'title': author.author.title,
    #             'url': author.author.url,
    #         } for author in opinion.authors.all()],
    #     })

    return JsonResponse({'opinions': len(opinions), 'op_eds': len(op_eds)})
