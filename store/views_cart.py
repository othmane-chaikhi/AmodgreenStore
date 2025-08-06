from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse
from django.http import JsonResponse
from urllib.parse import quote
from .models import Product, Category, Order, CommunityPost, Comment, CustomUser,Cart, CartItem
from .forms import OrderForm, CustomUserCreationForm, CommunityPostForm, CommentForm, UserProfileForm
from django.conf import settings

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{product.name} a été ajouté au panier.")
    return redirect('product_list')

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'store/cart.html', {'cart': cart})

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, "Produit retiré du panier.")
    return redirect('view_cart')

@login_required
def cart_summary(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    if cart.items.count() == 0:
        messages.warning(request, "Votre panier est vide.")
        return redirect('view_cart')

    total = sum(item.product.price * item.quantity for item in cart.items.all())
    return render(request, 'store/cart_summary.html', {'cart': cart, 'total': total})
