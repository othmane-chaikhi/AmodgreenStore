from django.utils.crypto import get_random_string
from .models import Cart

class GuestCartMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and 'guest_cart_id' not in request.session:
            # Create a unique session key for guest users
            request.session['guest_cart_id'] = get_random_string(32)
        
        response = self.get_response(request)
        return response