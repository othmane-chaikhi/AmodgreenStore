from django.contrib.sessions.models import Session
from .models import Cart

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        
        session = Session.objects.get(session_key=request.session.session_key)
        cart, created = Cart.objects.get_or_create(session=session)
    
    return cart