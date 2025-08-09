from .utils import get_or_create_cart  

def cart_count(request):
    cart = get_or_create_cart(request)
    return {'cart_count': cart.items.count()}