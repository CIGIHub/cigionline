from django import template

register = template.Library()


@register.filter
def article_series_category(article):
    category = ''
    for item in article.article_series.specific.series_items:
        if item.block_type == 'category_title':
            category = item.value
        else:
            if item.value.specific.id == article.id:
                return category
