from ..models import TopicPage
from django import template

register = template.Library()


@register.inclusion_tag('research/highlighted_topics.html')
def highlighted_topics():
    highlighted_topics = TopicPage.objects.live().filter(archive=0).order_by('title')
    return {'highlighted_topics': highlighted_topics}
