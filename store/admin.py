from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, Category, Product, ProductImage, ProductVariant, Order, CommunityPost

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'city', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'city')
    search_fields = ('username', 'first_name', 'last_name', 'email')

    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('bio', 'phone', 'city'),
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_ar', 'created_at')
    search_fields = ('name', 'name_ar')
    readonly_fields = ('created_at',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 10
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 8px;" />',
                obj.image.url
            )
        return "-"
    image_preview.short_description = "Aperçu"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

    list_display = ('name', 'category', 'price', 'is_available', 'image_preview', 'created_at')
    list_filter = ('category', 'is_available', 'created_at')
    search_fields = ('name', 'name_ar', 'description')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    list_editable = ('is_available', 'price')

    fieldsets = (
        ('Informations principales', {
            'fields': ('name', 'name_ar', 'category', 'price', 'is_available')
        }),
        ('Description', {
            'fields': ('description', 'description_ar', 'ingredients', 'ingredients_ar')
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 8px;" />',
                obj.image.url
            )
        return "Pas d'image"
    image_preview.short_description = "Aperçu"


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'price')
    list_filter = ('product',)
    search_fields = ('product__name', 'name')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at']
    list_display = ('id', 'full_name', 'phone', 'status', 'produits_commandes', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'phone', 'city')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Informations client', {
            'fields': ('full_name', 'phone', 'city', 'address')
        }),
        ('Statut et actions', {
            'fields': ('status',)
        }),
        ('Informations système', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def produits_commandes(self, obj):
        # Ici on utilise item.variant.product.name car OrderItem référence une variante
        return ", ".join([f"{item.variant.product.name} x{item.quantity}" for item in obj.items.all()])
    produits_commandes.short_description = "Produits"


@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_approved',)

    fieldsets = (
        ('Contenu', {
            'fields': ('author', 'title', 'content', 'post_type', 'product')
        }),
        ('Modération', {
            'fields': ('is_approved',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_posts', 'unapprove_posts']

    def approve_posts(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} post(s) approuvé(s).")
    approve_posts.short_description = "Approuver les posts sélectionnés"

    def unapprove_posts(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"{updated} post(s) désapprouvé(s).")
    unapprove_posts.short_description = "Désapprouver les posts sélectionnés"
