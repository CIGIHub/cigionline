from ..models import TopicPage
from django import template
from django.db.models import Count

register = template.Library()


@register.inclusion_tag('research/highlighted_topics.html', takes_context=True)
def highlighted_topics(context):
    highlighted_topics = TopicPage.objects.live().filter(archive=0).order_by('title').annotate(count=Count('content_pages'))
    return {
        'highlighted_topics': highlighted_topics,
        'request': context['request'],
    }


@register.inclusion_tag('research/topics.html')
def topics(topics):
    topics = topics.live().order_by('title')
    return {'topics': topics}
