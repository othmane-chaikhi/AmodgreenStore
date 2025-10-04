from django.shortcuts import get_object_or_404
from .models import Cart, Product

def get_or_create_cart(request):
    """Get or create a cart for authenticated or anonymous users"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key, user=None)
    return cart