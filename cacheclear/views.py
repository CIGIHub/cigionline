from django.shortcuts import render

def index(request):

    return render(request, 'index.html', {
        'hello': 'world',
    })

def clear_series_pages(request):
    print('hello')
    print(request)