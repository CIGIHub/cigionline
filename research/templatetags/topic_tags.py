from ..models import TopicPage
from django import template


register = template.Library()

@register.inclusion_tag('research/all_topics.html')
def all_topics():
    all_topics = TopicPage.objects.all()
    return {'all_topics': all_topics}
