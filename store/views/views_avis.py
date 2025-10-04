from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.contrib import messages

from store.models import Product, CommunityPost,ProductVariant, CartItem
from store.forms import CommunityPostForm

def product_reviews(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = CommunityPost.objects.filter(
        product=product,
        is_approved=True,
        rating__isnull=False
    ).order_by('-created_at')

    paginator = Paginator(reviews, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'store/product_reviews.html', {
        'product': product,
        'page_obj': page_obj,
    })

@login_required
def review_create(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = CommunityPostForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.product = product
            review.save()
            messages.success(request, "Votre avis a été ajouté et sera visible après validation.")
            return redirect('product_reviews', pk=product.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = CommunityPostForm(initial={'product': product})

    return render(request, 'store/review_form.html', {
        'form': form,
        'product': product,
    })

@login_required
def review_edit(request, review_id):
    review = get_object_or_404(CommunityPost, pk=review_id, author=request.user)

    if request.method == "POST":
        form = CommunityPostForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre avis a été mis à jour avec succès.")
            return redirect('product_detail', pk=review.product.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = CommunityPostForm(instance=review)

    return render(request, 'store/review_form.html', {
        'form': form,
        'product': review.product,
    })

@login_required
@require_POST
def review_delete(request, review_id):
    review = get_object_or_404(CommunityPost, pk=review_id, author=request.user)
    product_pk = review.product.pk
    review.delete()
    messages.success(request, "Votre avis a été supprimé.")
    return redirect('product_detail', pk=product_pk)
