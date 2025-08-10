from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.db.models import Prefetch
from django.db import transaction
import json
import openpyxl
from openpyxl.styles import Font, Alignment
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from store.forms import (
    ProductForm, ProductVariantFormSet, CategoryForm
)
from store.models import (
    Product, ProductVariant, ProductImage, Order, CommunityPost, Category
)

# --- Decorators ---
def admin_required(view_func):
    """Restrict access to admin users only."""
    return user_passes_test(lambda u: u.is_authenticated and u.is_superuser)(view_func)


# --- Dashboard ---
@admin_required
def admin_dashboard(request):
    orders_qs = Order.objects.filter(is_deleted=False).order_by('-created_at')
    orders = Paginator(orders_qs, 10).get_page(request.GET.get('order_page'))

    context = {
        'total_products': Product.objects.count(),
        'total_posts': CommunityPost.objects.count(),
        'orders_pending': orders_qs.filter(status='pending').count(),
        'orders_delivered': orders_qs.filter(status='delivered').count(),
        'products': Product.objects.order_by('-id')[:20],
        'orders': orders,
    }
    return render(request, 'admin/dashboard.html', context)


# --- Order Management ---
@admin_required
def update_order_status(request, order_id, status):
    Order.objects.filter(pk=order_id).update(status=status)
    messages.success(request, f"Statut de la commande #{order_id} mis à jour.")
    return redirect('admin_dashboard')


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    status_map = {'confirm': 'contacted', 'cancel': 'cancelled'}

    if request.method == 'POST':
        action = request.POST.get('action')
        if action in status_map:
            order.status = status_map[action]
            order.save()
            messages.success(request, f"Commande #{order.id} mise à jour.")
        return redirect('admin_dashboard')

    return render(request, 'admin/order_detail.html', {'order': order})


@admin_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        order.delete()
        messages.success(request, f"Commande #{order_id} supprimée définitivement.")
        return redirect('admin_dashboard')
    return render(request, 'admin/order_confirm_delete.html', {'order': order})


# --- Product Management ---
@admin_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        variant_formset = ProductVariantFormSet(request.POST, queryset=ProductVariant.objects.none())
        if form.is_valid() and variant_formset.is_valid():
            with transaction.atomic():
                product = form.save(commit=False)
                product.default_variant = None
                product.save()
                variant_formset.instance = product
                variants = variant_formset.save()
                for img in request.FILES.getlist('images'):
                    ProductImage.objects.create(product=product, image=img)
            messages.success(request, "Produit créé avec succès.")
            return redirect('admin_dashboard')
    else:
        form = ProductForm()
        variant_formset = ProductVariantFormSet(queryset=ProductVariant.objects.none())
    return render(request, 'admin/product_create.html', {'form': form, 'variant_formset': variant_formset})


@admin_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        variant_formset = ProductVariantFormSet(request.POST, instance=product)
        if form.is_valid() and variant_formset.is_valid():
            with transaction.atomic():
                variants = variant_formset.save(commit=False)
                for variant in variants:
                    variant.save()
                for deleted_form in variant_formset.deleted_forms:
                    if deleted_form.instance.pk:
                        deleted_form.instance.delete()

                default_variant_index = request.POST.get('default_variant')
                if default_variant_index is not None:
                    try:
                        product.variants.update(is_default=False)
                        default_variant_form = variant_formset.forms[int(default_variant_index)]
                        default_variant = default_variant_form.instance
                        default_variant.is_default = True
                        default_variant.save()
                        product.default_variant = default_variant
                    except (IndexError, ValueError):
                        product.default_variant = None
                else:
                    product.default_variant = None

                form.save()
                product.save()

                for img in request.FILES.getlist('images'):
                    ProductImage.objects.create(product=product, image=img)

            messages.success(request, "Produit mis à jour avec succès.")
            return redirect('admin_dashboard')
    else:
        form = ProductForm(instance=product)
        variant_formset = ProductVariantFormSet(instance=product)

    return render(request, 'admin/product_form.html', {
        'form': form,
        'variant_formset': variant_formset,
        'product': product,
        'images': product.additional_images.all(),
        'title': 'Modifier le produit',
    })


@csrf_protect
@admin_required
def delete_product_image(request, pk):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Méthode non autorisée"})
    try:
        data = json.loads(request.body)
        img_id = data.get("id")
        img_type = data.get("type")
        product = get_object_or_404(Product, pk=pk)

        if img_type == "main" and product.image:
            product.image.delete(save=False)
            product.image = None
            product.save()
            return JsonResponse({"success": True})

        elif img_type == "extra":
            img = get_object_or_404(ProductImage, id=img_id, product=product)
            img.image.delete(save=False)
            img.delete()
            return JsonResponse({"success": True})

        return JsonResponse({"success": False, "error": "Type d'image invalide"})
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Données JSON invalides"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@admin_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Produit supprimé avec succès.")
        return redirect('admin_dashboard')
    return render(request, 'admin/product_confirm_delete.html', {'product': product})


# --- Export ---
@admin_required
def export_orders_excel(request):
    orders = Order.objects.prefetch_related(Prefetch('items', to_attr='prefetched_items')).order_by("-created_at")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Commandes"

    headers = ["ID", "Nom Client", "Téléphone", "Adresse", "Statut", "Date", "Produit", "Quantité"]
    ws.append(headers)
    for col in ws[1]:
        col.font = Font(bold=True)
        col.alignment = Alignment(horizontal="center")

    row_num = 2
    for order in orders:
        items = getattr(order, 'prefetched_items', [])
        if items:
            start_row = row_num
            for item in items:
                ws.cell(row=row_num, column=7, value=item.product.name)
                ws.cell(row=row_num, column=8, value=item.quantity)
                row_num += 1
            for col in range(1, 7):
                ws.merge_cells(start_row=start_row, start_column=col, end_row=row_num - 1, end_column=col)
            ws.cell(row=start_row, column=1, value=order.id)
            ws.cell(row=start_row, column=2, value=order.full_name)
            ws.cell(row=start_row, column=3, value=order.phone)
            ws.cell(row=start_row, column=4, value=order.address)
            ws.cell(row=start_row, column=5, value=order.get_status_display())
            ws.cell(row=start_row, column=6, value=order.created_at.strftime("%d/%m/%Y %H:%M"))
        else:
            ws.append([
                order.id, order.full_name, order.phone, order.address,
                order.get_status_display(), order.created_at.strftime("%d/%m/%Y %H:%M"),
                "Aucun produit", "-"
            ])
            row_num += 1

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=commandes.xlsx'
    wb.save(response)
    return response


@admin_required
def export_orders_pdf(request):
    orders = Order.objects.prefetch_related(Prefetch('items', to_attr='prefetched_items')).order_by("-created_at")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=commandes.pdf'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    for order in orders:
        elements.append(Paragraph(f"Commande #{order.id}", styles["Heading1"]))
        elements.append(Paragraph(f"Client : {order.full_name}", styles["Normal"]))
        elements.append(Paragraph(f"Téléphone : {order.phone}", styles["Normal"]))
        elements.append(Paragraph(f"Adresse : {order.address}", styles["Normal"]))

        status_style = styles["Normal"]
        if order.status == 'cancelled':
            status_style = ParagraphStyle("CancelledStyle", parent=status_style, textColor=colors.red)
        elif order.status == 'delivered':
            status_style = ParagraphStyle("DeliveredStyle", parent=status_style, textColor=colors.green)

        elements.append(Paragraph(f"Statut : {order.get_status_display()}", status_style))
        elements.append(Paragraph(f"Date : {order.created_at.strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        data = [["Produit", "Quantité"]] + [[item.product.name, item.quantity] for item in order.prefetched_items]
        if len(data) > 1:
            table = Table(data, colWidths=[300, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("Aucun produit commandé", styles["Normal"]))
        elements.append(Spacer(1, 24))

    doc.build(elements)
    return response


# --- Category ---
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


# --- Order Confirmation ---
@login_required
def confirm_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    order.status = 'confirmed'
    order.save()
    messages.success(request, "Commande confirmée avec succès.")
    return redirect('admin_dashboard')
