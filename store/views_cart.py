from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.conf import settings
from .models import Product, Cart, CartItem
from .utils import get_or_create_cart


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{product.name} a été ajouté au panier.")
    return redirect('product_list')


def view_cart(request):
    cart = get_or_create_cart(request)
    return render(request, 'store/cart.html', {'cart': cart})


def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    messages.success(request, "Produit retiré du panier.")
    return redirect('view_cart')


def cart_summary(request):
    cart = get_or_create_cart(request)
    if cart.items.count() == 0:
        messages.warning(request, "Votre panier est vide.")
        return redirect('view_cart')

    total = sum(item.product.price * item.quantity for item in cart.items.all())
    return render(request, 'store/cart_summary.html', {'cart': cart, 'total': total})
