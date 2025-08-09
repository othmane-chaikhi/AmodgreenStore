import os
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.contrib.sessions.models import Session
from .models import Cart, Product, ProductImage, Order, CommunityPost
from .telegram import send_telegram_message


@receiver(pre_save, sender=Session)
def delete_anonymous_carts(sender, instance, **kwargs):
    """
    Supprime les paniers anonymes liés à la session avant sauvegarde de celle-ci.
    """
    Cart.objects.filter(session_key=instance.session_key, user__isnull=True).delete()


@receiver(post_save, sender=Order)
def notify_order_created(sender, instance, created, **kwargs):
    if created:
        items = instance.items.all()
        if items.exists():
            message = f"Nouvelle commande #{instance.pk} avec {items.count()} article(s)."
            send_telegram_message(message)


@receiver(post_save, sender=CommunityPost)
def notify_new_post(sender, instance, created, **kwargs):
    if created:
        title = instance.title
        author = instance.author.username
        message = (
            f"🗣️ منشور جديد في المجتمع: <b>{title}</b>\n"
            f"👤 من طرف: <b>{author}</b>\n"
        )
        send_telegram_message(message)


@receiver(post_delete, sender=Product)
def delete_product_image_files(sender, instance, **kwargs):
    """Supprime le fichier image principale du disque après suppression du produit."""
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)


@receiver(post_delete, sender=ProductImage)
def delete_productimage_file(sender, instance, **kwargs):
    """Supprime le fichier image secondaire du disque après suppression de l'image."""
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)


@receiver(post_delete, sender=CommunityPost)
def delete_review_image_file(sender, instance, **kwargs):
    """Supprime l'image du disque après suppression d'un avis."""
    if instance.image and os.path.isfile(instance.image.path):
        try:
            os.remove(instance.image.path)
        except FileNotFoundError:
            pass
