from django.shortcuts import render

# Create your views here.


def index(request):
    panels = [
      
    ]
    for panel in panels:
        if hasattr(panel, 'media'):
            media += panel.media

    return render(request, 'caching/index.html', {
        'title': 'Caching'
    })
