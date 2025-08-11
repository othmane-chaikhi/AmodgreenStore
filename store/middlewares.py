from django.http import HttpResponseNotFound
from django.shortcuts import render

class MediaNotFoundMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404 and request.path.startswith('/media/'):
            return render(request, 'errors/404.html', {
                'custom_message': "L'image demandée n'est plus disponible"
            }, status=404)
        return response