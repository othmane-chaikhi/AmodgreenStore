from urllib.parse import quote

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.conf import settings

from store.models import (
    Product, Category, Order, OrderItem,
    CommunityPost, CustomUser, Cart, ProductVariant, CartItem
)
from store.forms import (
    OrderForm, CustomUserCreationForm, CommunityPostForm,
    UserProfileForm
)
from store.utils import get_or_create_cart
from store.telegram import send_telegram_message


def home(request):
    featured_products = Product.objects.filter(is_available=True)[:6]
    latest_reviews = CommunityPost.objects.filter(is_approved=True)[:5]

    context = {
        'featured_products': featured_products,
        'latest_reviews': latest_reviews,
        'total_products': Product.objects.filter(is_available=True).count(),
        'total_categories': Category.objects.count(),
    }
    return render(request, 'store/home.html', context)


def product_list(request):
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()

    category_id = request.GET.get('category')
    search_query = request.GET.get('search')

    if category_id:
        products = products.filter(category_id=category_id)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(name_ar__icontains=search_query)
        )

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': int(category_id) if category_id else None,
        'search_query': search_query or '',
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_available=True)
    # product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(pk=product.pk)[:4]

    product_reviews = CommunityPost.objects.filter(
        product=product,
        is_approved=True,
        rating__isnull=False
    ).order_by('-created_at')[:5]

    reviews_stats = product_reviews.aggregate(
        avg_rating=Avg('rating'),
        count=Count('id')
    )

    # Utilisation de la méthode sans filtrer sur stock
    variants = product.available_variants()

    if request.method == 'POST' and 'submit_review' in request.POST:
        if not request.user.is_authenticated:
            messages.warning(request, "Vous devez être connecté pour poster un avis.")
            return redirect(f"{request.build_absolute_uri('/accounts/login/')}?next={request.path}")

        form = CommunityPostForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.product = product
            review.is_approved = True
            review.save()
            messages.success(request, "Votre avis a été ajouté avec succès !")
            return redirect('product_detail', pk=product.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = CommunityPostForm(initial={'product': product.id})

    context = {
        'product': product,
        'variants': variants,
        'related_products': related_products,
        'product_reviews': product_reviews,
        'avg_rating': round(reviews_stats['avg_rating'], 1) if reviews_stats['avg_rating'] else None,
        'review_count': reviews_stats['count'],
        'review_form': form,
    }
    return render(request, 'store/product_detail.html', context)


def order_create(request):
    cart = get_or_create_cart(request)
    if not cart or not cart.items.exists():
        messages.warning(request, "Votre panier est vide.")
        return redirect('view_cart')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()

            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    variant=item.variant,
                    quantity=item.quantity,
                    price=item.variant.price,
                )
            cart.items.all().delete()
            if not request.user.is_authenticated:
                cart.delete()

            items_text = "\n".join([
                f"• {item.variant.product.name} ({item.variant.name}) x{item.quantity} = {item.price} درهم"
                for item in order.items.all()
            ])
            message = f"""🛒 <b>طلب جديد!</b>
<b>_Commande #{order.id} - {order.created_at.strftime('%d/%m/%Y à %H:%M')}_</b>
👤 <b>العميل:</b> {order.full_name}
📞 <b>الهاتف:</b> {order.phone}
🏙️ <b>المدينة:</b> {order.city}
💰 <b>المجموع:</b> {order.total_price} درهم
🛍️ <b>المنتجات:</b>
{items_text}

⛔⛔⛔ <b>Remarques:</b> {order.notes if order.notes else 'Aucune'} ⛔⛔⛔"""
            send_telegram_message(message)

            whatsapp_url = f"https://wa.me/{settings.ADMIN_WHATSAPP_NUMBER}?text={quote(generate_order_message(order))}"
            messages.success(request, 'Votre commande a été envoyée avec succès !')
            return render(request, 'store/order_success.html', {
                'order': order,
                'whatsapp_url': whatsapp_url
            })
    else:
        form = OrderForm()

    return render(request, 'store/order_form.html', {
        'form': form,
        'cart': cart,
    })


def generate_order_message(order):
    items_text = "\n".join(
        [f"📦 {item.quantity}x {item.variant.product.name} ({item.variant.name}) ({item.price} MAD)"
         for item in order.items.all()]
    )
    total = sum(item.quantity * item.price for item in order.items.all())

    return f"""🌿 *Nouvelle commande AmodIgren* 🌿

👤 *Client:* {order.full_name}
📱 *Téléphone:* {order.phone}   
🏙️ *Ville:* {order.city}
📍 *Adresse:* {order.address}

🛒 *Articles:*
{items_text}

💰 *Total:* {total} MAD
📝 *Remarques:* {order.notes if order.notes else 'Aucune'}

_Commande #{order.id} - {order.created_at.strftime('%d/%m/%Y à %H:%M')}_"""


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bienvenue {user.first_name}! Votre compte a été créé avec succès.')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    user_posts = CommunityPost.objects.filter(author=request.user).order_by('-created_at')

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'store/profile.html', {
        'form': form,
        'user_posts': user_posts,
    })


def about(request):
    return render(request, 'store/about.html')


def contact(request):
    return render(request, 'store/contact.html')


