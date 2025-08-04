from django.urls import path
from . import views
from . import views_admin


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
    
    # Communauté
    path('communaute/', views.community, name='community'),
    path('communaute/nouveau-post/', views.create_post, name='create_post'),
    path('communaute/commenter/<int:post_id>/', views.add_comment, name='add_comment'),
    
    # Profil utilisateur
    path('profil/', views.profile, name='profile'),

    path('admin-dashboard/', views_admin.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/order/<int:order_id>/<str:status>/', views_admin.update_order_status, name='update_order_status'),
    path('admin-dashboard/comment/<int:comment_id>/toggle/', views_admin.toggle_comment_approval, name='toggle_comment_approval'),
]