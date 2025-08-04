from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, CommunityPost, Comment
from .forms import ProductForm

# Vérifie si l'utilisateur est superuser
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.is_superuser)(view_func)


@admin_required
def admin_dashboard(request):
    orders = Order.objects.all()
    comments = Comment.objects.all()
    posts = CommunityPost.objects.all()
    products = Product.objects.all()

    return render(request, 'admin/dashboard.html', {
        'orders': orders,
        'comments': comments,
        'products': products,
        'posts': posts,
    })


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
