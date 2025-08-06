from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse
from django.http import JsonResponse
from urllib.parse import quote
from .models import Product, Category, Order, CommunityPost, Comment, CustomUser, Order, OrderItem ,Cart
from .forms import OrderForm, CustomUserCreationForm, CommunityPostForm, CommentForm, UserProfileForm
from django.conf import settings

def home(request):
    """Page d'accueil"""
    # Produits en vedette (les 6 derniers)
    featured_products = Product.objects.filter(is_available=True)[:6]
    
    # Derniers avis approuvés de la communauté
    latest_reviews = CommunityPost.objects.filter(
        is_approved=True,
        post_type='review'
    )[:5]
    
    # Statistiques pour l'affichage
    total_products = Product.objects.filter(is_available=True).count()
    total_categories = Category.objects.count()
    
    context = {
        'featured_products': featured_products,
        'latest_reviews': latest_reviews,
        'total_products': total_products,
        'total_categories': total_categories,
    }
    return render(request, 'store/home.html', context)

def product_list(request):
    """Liste des produits avec filtres"""
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    
    # Filtres
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
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 produits par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': int(category_id) if category_id else None,
        'search_query': search_query or '',
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, pk):
    """Détail d'un produit"""
    product = get_object_or_404(Product, pk=pk, is_available=True)
    
    # Produits similaires
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(pk=product.pk)[:4]
    
    # Avis sur ce produit
    product_reviews = CommunityPost.objects.filter(
        product=product,
        is_approved=True,
        post_type='review'
    )[:3]
    
    context = {
        'product': product,
        'related_products': related_products,
        'product_reviews': product_reviews,
    }
    return render(request, 'store/product_detail.html', context)

def order_create(request):
    """Créer une commande avec tous les produits du panier"""
    cart = getattr(request.user, 'cart', None)
    if not cart or not cart.items.exists():
        messages.warning(request, "Votre panier est vide.")
        return redirect('cart')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Créer la commande sans produit/quantité
            order = form.save(commit=False)
            order.save()

            # Créer les OrderItems
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                )

            # Vider le panier
            cart.items.all().delete()

            # Message WhatsApp
            admin_phone = settings.ADMIN_WHATSAPP_NUMBER
            message = generate_order_message(order)
            whatsapp_url = f"https://wa.me/{admin_phone}?text={quote(message)}"

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
    """Message WhatsApp regroupant tous les articles de la commande"""
    items_text = "\n".join(
        [f"📦 {item.quantity}x {item.product.name} ({item.price} MAD)" for item in order.items.all()]
    )
    total = sum([item.quantity * item.price for item in order.items.all()])
    return f"""🌿 *Nouvelle commande AmodGreen* 🌿

    👤 *Client:* {order.full_name}
    📱 *Téléphone:* {order.phone}
    🏙️ *Ville:* {order.city}
    📍 *Adresse:* {order.address}

    🛒 *Articles:*
    {items_text}

    💰 *Total:* {total} MAD
    📝 *Remarques:* {order.notes if order.notes else 'Aucune'}

    _Commande #_{order.id} - {order.created_at.strftime('%d/%m/%Y à %H:%M')}_"""

def register_view(request):
    """Inscription d'un nouvel utilisateur"""
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

def community(request):
    """Page communauté avec posts filtrés, pagination et formulaires pour utilisateur connecté."""
    post_type = request.GET.get('type')

    # Récupérer les posts approuvés, filtrer par type si spécifié
    posts = CommunityPost.objects.filter(is_approved=True)
    if post_type in ['review', 'testimonial', 'discussion']:
        posts = posts.filter(post_type=post_type)
    
    posts = posts.order_by('-created_at')

    # Pagination (10 posts par page)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Formulaires affichés uniquement si utilisateur connecté
    post_form = CommunityPostForm() if request.user.is_authenticated else None
    comment_form = CommentForm() if request.user.is_authenticated else None

    context = {
        'page_obj': page_obj,
        'post_form': post_form,
        'comment_form': comment_form,
        'current_type': post_type,
    }
    return render(request, 'store/community.html', context)

@login_required
def create_post(request):
    """Créer un nouveau post communauté"""
    if request.method == 'POST':
        form = CommunityPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Votre message a été soumis et sera publié après modération.')
            return redirect('community')
    
    return redirect('community')

@login_required
def add_comment(request, post_id):
    """Ajouter un commentaire à un post"""
    if request.method == 'POST':
        post = get_object_or_404(CommunityPost, pk=post_id, is_approved=True)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Votre commentaire a été soumis et sera publié après modération.')
    
    return redirect('community')

@login_required
def profile(request):
    """Profil utilisateur"""
    user_posts = CommunityPost.objects.filter(author=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'user_posts': user_posts,
    }
    return render(request, 'store/profile.html', context)

def about(request):
    """Page à propos"""
    return render(request, 'store/about.html')

def contact(request):
    """Page contact"""
    return render(request, 'store/contact.html')
