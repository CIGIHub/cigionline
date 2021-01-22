from ..models import TopicPage, ContentPage
from django import template
from django.db.models import Count

register = template.Library()


@register.inclusion_tag('research/highlighted_topics.html')
def highlighted_topics():
    highlighted_topics = TopicPage.objects.live().filter(archive=0).order_by('title')
    annotated_topics = TopicPage.objects.live().filter(archive=0).annotate(count=Count('contentpage'))
    return {'highlighted_topics': highlighted_topics, 'annotated_topics': annotated_topics}


@register.inclusion_tag('research/topics.html')
def topics(topics):
    topics = topics.live().order_by('title')
    return {'topics': topics}


# @register.simple_tag
# def topic_content(topic):
#     return ContentPage.objects.live().filter(topics__contains=topic)
