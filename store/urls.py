from django.urls import path
from .views import views, views_admin, views_cart, views_avis
from django.conf.urls import handler404, handler500
from .views import views_errors

handler404 = views_errors.handler404
handler500 = views_errors.handler500

urlpatterns = [
    # Pages principales
    path('', views.home, name='home'),
    path('produits/', views.product_list, name='product_list'),
    path('produit/<int:pk>/', views.product_detail, name='product_detail'),
    path('commander/', views.order_create, name='order_create'),
    path('a-propos/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # Authentification
    path('inscription/', views.register_view, name='register'),
    path('profil/', views.profile, name='profile'),

    # Panier
    path('cart/', views_cart.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views_cart.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views_cart.remove_from_cart, name='remove_from_cart'),
    path('cart/summary/', views_cart.cart_summary, name='cart_summary'),
    path('direct_order/<int:product_id>/', views.direct_order, name='direct_order'),
    path('order/review/<int:order_id>/', views.order_review, name='order_review'),
    # Admin dashboard & gestion
    path('admin-dashboard/', views_admin.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/product/create/', views_admin.product_create, name='product_create'),
    path('admin-dashboard/product/<int:pk>/update/', views_admin.product_update, name='product_update'),
    path('admin-dashboard/product/<int:pk>/delete/', views_admin.product_delete, name='product_delete'),
    path('admin-dashboard/category/create/', views_admin.category_create, name='category_create'),
    path('categories/', views_admin.category_list, name='category_list'),
    path('categories/<int:pk>/update/', views_admin.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views_admin.category_delete, name='category_delete'),
    path('admin-dashboard/categories/', views_admin.category_list, name='category_list'),
    path('admin-dashboard/orders/', views_admin.order_list, name='order_list'),
    path('admin-dashboard/posts/', views_admin.post_list, name='post_list'),
    path('admin-dashboard/produits/', views_admin.admin_product_list, name='admin_product_list'),
    path('admin-dashboard/order/<int:order_id>/', views_admin.order_detail, name='order_detail'),
    path('admin-dashboard/order/<int:order_id>/contact/', views_admin.contact_customer, name='contact_customer'),
    path('admin-dashboard/order/<int:order_id>/<str:status>/', views_admin.update_order_status, name='update_order_status'),
    path('admin-dashboard/orders/delete/<int:order_id>/', views_admin.delete_order, name='delete_order'),
    path('admin-dashboard/orders/restore/<int:order_id>/', views_admin.restore_order, name='restore_order'),

    # Pour la gestion des images et modification produit
    path('product/<int:pk>/edit/', views_admin.product_update, name='product_update'),
    path('product/<int:pk>/delete-image/', views_admin.delete_product_image, name='delete_product_image'),

    # Exportation
    path('admin-dashboard/export/pdf/', views_admin.export_orders_pdf, name='export_orders_pdf'),
    path('admin-dashboard/export/excel/', views_admin.export_orders_excel, name='export_orders_excel'),

    # Avis produit
    path('produit/<int:pk>/avis/ajouter/', views_avis.review_create, name='review_create'),
    path('avis/<int:review_id>/modifier/', views_avis.review_edit, name='review_edit'),
    path('avis/<int:review_id>/supprimer/', views_avis.review_delete, name='review_delete'),
    path('produit/<int:pk>/avis/', views_avis.product_reviews, name='product_reviews'),
]
