import os
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.contrib.sessions.models import Session
from store.models import Cart, Product, ProductImage, Order, CommunityPost, ProductVariant
from .telegram import send_telegram_message


# 🛒 Supprimer les paniers anonymes liés à une session supprimée
@receiver(pre_save, sender=Session)
def delete_anonymous_carts(sender, instance, **kwargs):
    Cart.objects.filter(session_key=instance.session_key, user__isnull=True).delete()


# 📦 Notifier quand une commande est créée
@receiver(post_save, sender=Order)
def notify_order_created(sender, instance, created, **kwargs):
    if created and instance.items.count() > 0:
        message = f"Nouvelle commande #{instance.pk} avec {instance.items.count()} article(s)."
        send_telegram_message(message)


# 🗣️ Notifier quand un avis est créé
@receiver(post_save, sender=CommunityPost)
def notify_new_post(sender, instance, created, **kwargs):
    if created:
        message = (
            f"🗣️ Avis produit: <b>{instance.title}</b>\n"
            f"👤 Auteur: <b>{instance.author.username}</b>\n"
        )
        send_telegram_message(message)


# 🖼️ Supprimer l'image principale d'un produit supprimé
@receiver(post_delete, sender=Product)
def delete_product_image_files(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        try:
            os.remove(instance.image.path)
        except FileNotFoundError:
            pass


# 🖼️ Supprimer les images supplémentaires d'un produit supprimé
@receiver(post_delete, sender=ProductImage)
def delete_productimage_file(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        try:
            os.remove(instance.image.path)
        except FileNotFoundError:
            pass


# 🖼️ Supprimer l'image d'un avis supprimé
@receiver(post_delete, sender=CommunityPost)
def delete_review_image_file(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        try:
            os.remove(instance.image.path)
        except FileNotFoundError:
            pass


# 🔄 Supprimer l'ancienne image d'un avis si elle est remplacée
@receiver(pre_save, sender=CommunityPost)
def auto_delete_old_review_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_image = CommunityPost.objects.get(pk=instance.pk).image
    except CommunityPost.DoesNotExist:
        return
    new_image = instance.image
    if old_image and old_image != new_image and os.path.isfile(old_image.path):
        try:
            os.remove(old_image.path)
        except FileNotFoundError:
            pass


# ⚙️ Gérer la variante par défaut d'un produit
@receiver(post_save, sender=ProductVariant)
def update_default_variant(sender, instance, **kwargs):
    if instance.is_default:
        ProductVariant.objects.filter(
            product=instance.product
        ).exclude(pk=instance.pk).update(is_default=False)
        instance.product.default_variant = instance
        instance.product.save(update_fields=['default_variant'])
