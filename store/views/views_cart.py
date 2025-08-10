from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from ..models import Product, ProductVariant, CartItem
from ..utils import get_or_create_cart  # adapte le chemin si besoin


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variants = ProductVariant.objects.filter(product=product)

    if not variants.exists():
        # Create a default variant if none exists
        variant, created = ProductVariant.objects.get_or_create(
            product=product,
            name="Standard",
            defaults={
                'price': product.price, 
                'stock': 9999,
                'is_default': True  # Mark as default
            }
        )
        # Update product's default variant reference
        product.default_variant = variant
        product.save(update_fields=['default_variant'])
    else:
        variant_id = request.POST.get('variant_id')
        
        # If no variant selected, use the product's current default variant
        if not variant_id:
            variant = product.default_variant
            if not variant:
                # If no default variant set, use the first available variant
                variant = variants.first()
                # Set it as default if not already
                if not variant.is_default:
                    variant.is_default = True
                    variant.save()
                    product.default_variant = variant
                    product.save(update_fields=['default_variant'])
                messages.info(request, f"Variante '{variant.name}' sélectionnée par défaut")
        else:
            variant = get_object_or_404(ProductVariant, id=variant_id, product=product)

    cart = get_or_create_cart(request)

    # Check stock availability
    if variant.stock <= 0:
        messages.error(request, f"La variante '{variant.name}' est en rupture de stock.")
        return redirect(product.get_absolute_url())

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        variant=variant,
        defaults={'quantity': 1}
    )
    
    if not created:
        # Check if adding more would exceed stock
        if cart_item.quantity + 1 > variant.stock:
            messages.error(request, f"Quantité demandée non disponible pour '{variant.name}' (stock: {variant.stock})")
            return redirect(product.get_absolute_url())
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"Le produit '{product.name}' ({variant.name}) a été ajouté au panier.")
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

    if not cart.items.exists():
        messages.warning(request, "Votre panier est vide.")
        return redirect('view_cart')

    total = sum(item.variant.price * item.quantity for item in cart.items.all())

    return render(request, 'store/cart_summary.html', {
        'cart': cart,
        'total': total,
    })
