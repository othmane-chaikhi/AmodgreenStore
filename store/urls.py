from django.urls import path
from . import views, views_admin, views_cart

urlpatterns = [
    # Pages principales
    path('', views.home, name='home'),
    path('produits/', views.product_list, name='product_list'),
    path('produit/<int:pk>/', views.product_detail, name='product_detail'),
    path('produit/<int:pk>/avis/', views.product_reviews, name='product_reviews'),
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
    path('cart/recapitulatif/', views_cart.cart_summary, name='cart_summary'),  # يمكن حذف واحدة إذا رغبت

    # Communauté
    # path('communaute/', views.community, name='community'),
    # path('communaute/nouveau-post/', views.create_post, name='create_post'),
    # path('communaute/commenter/<int:post_id>/', views.add_comment, name='add_comment'),

    # Admin dashboard & gestion
    path('admin-dashboard/', views_admin.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/product/create/', views_admin.product_create, name='product_create'),
    path('admin-dashboard/product/<int:pk>/update/', views_admin.product_update, name='product_update'),
    path('admin-dashboard/product/<int:pk>/delete/', views_admin.product_delete, name='product_delete'),

    path('admin-dashboard/category/create/', views_admin.category_create, name='category_create'),

    path('admin-dashboard/order/<int:order_id>/', views_admin.order_detail, name='order_detail'),
    path('admin-dashboard/order/<int:order_id>/confirm/', views_admin.confirm_order, name='confirm_order'),
    path('admin-dashboard/order/<int:order_id>/<str:status>/', views_admin.update_order_status, name='update_order_status'),
    path('admin-dashboard/orders/delete/<int:order_id>/', views_admin.delete_order, name='delete_order'),

    # path('admin-dashboard/comment/<int:comment_id>/toggle/', views_admin.toggle_comment_approval, name='toggle_comment_approval'),

    path('product/<int:pk>/edit/', views_admin.product_update, name='product_update'),
    path('product/<int:pk>/delete-image/', views_admin.delete_product_image, name='delete_product_image'),

    # Exportation
    path('admin-dashboard/export/pdf/', views_admin.export_orders_pdf, name='export_orders_pdf'),
    path('admin-dashboard/export/excel/', views_admin.export_orders_excel, name='export_orders_excel'),
]
