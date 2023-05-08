from ..models import TopicPage
from django import template
from django.db.models import Count

register = template.Library()


@register.inclusion_tag('research/highlighted_topics.html', takes_context=True)
def highlighted_topics(context):
    highlighted_topics = TopicPage.objects.live().filter(archive=0).order_by('title').annotate(count=Count('content_pages'))
    result = {
        'highlighted_topics': highlighted_topics,
    }
    if context and hasattr(context, 'request'):
        result['request'] = context['request']
    return result


@register.inclusion_tag('research/highlighted_topics_footer.html', takes_context=True)
def highlighted_topics_footer(context):
    highlighted_topics = TopicPage.objects.live().filter(archive=0).order_by('title').annotate(count=Count('content_pages'))
    result = {
        'highlighted_topics': highlighted_topics,
    }
    if context and hasattr(context, 'request'):
        result['request'] = context['request']
    return result


@register.inclusion_tag('research/topics.html')
def topics(topics):
    topics = topics.live().order_by('title')
    return {'topics': topics}


@register.inclusion_tag('research/top_topics.html')
def top_topics(issues=None, live_events=None):
    topics = TopicPage.objects.live().filter(archive=0).annotate(num_content_pages=Count('content_pages')).order_by('-num_content_pages')
    return {'topics': topics, 'issues': issues, 'live_events': live_events}
