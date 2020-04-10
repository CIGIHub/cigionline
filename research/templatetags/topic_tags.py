from django import template
register = template.Library()

from ..models import TopicPage

@register.inclusion_tag('research/all_topics.html')
def all_topics():
  all_topics = TopicPage.objects.all()
  print(all_topics)
  return {'all_topics' : all_topics}
