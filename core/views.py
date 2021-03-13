from django.http import JsonResponse


def cookie_consent(request):
    request.session['cookie_consent'] = True
    return JsonResponse({})
