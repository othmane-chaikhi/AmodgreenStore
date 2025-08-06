from django.contrib.auth.decorators import user_passes_test,login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponse
from .forms import ProductForm,ConfirmOrderForm,CategoryForm
from .models import Product, Order, CommunityPost, Comment
import openpyxl

# Vérifie si l'utilisateur est superuser
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.is_superuser)(view_func)

@admin_required
def admin_dashboard(request):
    # Statistiques
    total_products = Product.objects.count()
    total_comments = Comment.objects.count()
    total_posts = CommunityPost.objects.count()
    orders_pending = Order.objects.filter(status='pending').count()
    orders_delivered = Order.objects.filter(status='delivered').count()

    # Produits
    products = Product.objects.all().order_by('-id')

    # Pagination des commandes
    orders_all = Order.objects.filter(is_deleted=False).order_by('-created_at') 
    order_page_number = request.GET.get('order_page')
    orders_paginator = Paginator(orders_all, 10)
    orders = orders_paginator.get_page(order_page_number)

    context = {
        'total_products': total_products,
        'total_comments': total_comments,
        'total_posts': total_posts,
        'orders_pending': orders_pending,
        'orders_delivered': orders_delivered,
        'products': products[:20],  # Garde les 20 produits récents
        'orders': orders,
    }
    return render(request, 'admin/dashboard.html', context)

@admin_required
def update_order_status(request, order_id, status):
    order = get_object_or_404(Order, pk=order_id)
    order.status = status
    order.save()
    return redirect('admin_dashboard')

@admin_required
def toggle_comment_approval(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.is_approved = not comment.is_approved
    comment.save()
    return redirect('admin_dashboard')

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.is_superuser)(view_func)

@admin_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')  # redirige vers le dashboard après création
    else:
        form = ProductForm()
    
    return render(request, 'admin/product_create.html', {'form': form})

@admin_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'admin/product_form.html', {'form': form, 'title': 'Modifier le produit'})

@admin_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('admin_dashboard')
    return render(request, 'admin/product_confirm_delete.html', {'product': product})

@admin_required
def confirm_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if request.method == 'POST':
        # action: confirmer la commande
        order.status = 'contacted'
        order.save()
        messages.success(request, f"La commande de {order.full_name} a été confirmée.")
        return redirect('admin_dashboard')  # rediriger vers dashboard

    # sinon GET = afficher la page de détails
    return render(request, 'admin/order_detail.html', {'order': order})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if request.method == 'POST':
        # Confirmer la commande
        action = request.POST.get('action')
        if action == 'confirm':
            order.status = 'contacted'  # ou 'confirmed' selon ton modèle
            order.save()
            messages.success(request, f"Commande #{order.id} confirmée.")
        elif action == 'cancel':
            order.status = 'cancelled'
            order.save()
            messages.success(request, f"Commande #{order.id} annulée.")
        return redirect('admin_dashboard')  # ou vers un autre endroit

    # Si GET, afficher les détails
    return render(request, 'admin/order_detail.html', {'order': order})

@admin_required
def delete_order(request, order_id):
    if request.method != 'POST':
        messages.error(request, "Suppression non autorisée.")
        return redirect('admin_dashboard')

    order = get_object_or_404(Order, pk=order_id)
    order.is_deleted = True
    order.status = 'deleted'
    order.save()
    messages.success(request, f"Commande #{order_id} marquée comme supprimée.")
    return redirect('admin_dashboard')

def export_orders_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Commandes"

    # En-têtes
    headers = ["ID", "Nom Client", "Produit", "Quantité", "Adresse", "Statut", "Date"]
    ws.append(headers)

    # Données
    for order in Order.objects.all():
        ws.append([
            order.id,
            order.full_name,
            order.product.name,
            order.quantity,
            order.address,
            order.get_status_display(),
            order.created_at.strftime("%d/%m/%Y %H:%M")
        ])

    # Réponse HTTP
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=commandes.xlsx'
    wb.save(response)
    return response

@admin_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie ajoutée avec succès.")
            return redirect('admin_dashboard')
    else:
        form = CategoryForm()
    return render(request, 'admin/category_form.html', {'form': form})