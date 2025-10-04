from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from ..models import Product, ProductVariant, CartItem
from ..utils import get_or_create_cart


# -------------------- CART VIEWS --------------------
def view_cart(request):
    """Afficher le contenu du panier."""
    cart = get_or_create_cart(request)
    return render(request, 'store/cart.html', {'cart': cart})


def add_to_cart(request, product_id):
    """Ajouter un produit (et variante) au panier."""
    product = get_object_or_404(Product, id=product_id)
    variants = ProductVariant.objects.filter(product=product)

    # Récupérer la variante
    variant_id = request.POST.get('variant_id')
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
    else:
        variant = product.default_variant or variants.first()
        if not variant:
            messages.error(request, "Produit ou variante non disponible.")
            return redirect('product_detail', pk=product.id)

    # Récupérer la quantité
    try:
        quantity = int(request.POST.get('quantity', 1))
        quantity = max(quantity, 1)
    except (TypeError, ValueError):
        quantity = 1

    # Créer ou mettre à jour le CartItem
    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        variant=variant,
        defaults={'quantity': quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    messages.success(request, f"'{product.name}' ({variant.name}) ajouté au panier.")
    return redirect('product_list')


def remove_from_cart(request, item_id):
    """Supprimer un article du panier."""
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    messages.success(request, "Produit retiré du panier.")
    return redirect('view_cart')


def cart_summary(request):
    """Résumé et validation du panier."""
    cart = get_or_create_cart(request)

    if not cart.items.exists():
        messages.warning(request, "Votre panier est vide.")
        return redirect('view_cart')

    total = sum(item.variant.price * item.quantity for item in cart.items.all())

    return render(request, 'store/cart_summary.html', {
        'cart': cart,
        'total': total,
    })
