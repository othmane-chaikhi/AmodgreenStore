from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.sessions.models import Session
from .models import Cart

@receiver(pre_save, sender=Session)
def delete_anonymous_carts(sender, instance, **kwargs):
    """
    Delete anonymous carts when their session is being cleared/overwritten.
    """
    Cart.objects.filter(session_key=instance.session_key, user__isnull=True).delete()

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .telegram import send_telegram_message

@receiver(post_save, sender=Order)
def notify_order_created(sender, instance, created, **kwargs):
    if created:
        order = instance
        items = order.items.all()
        
        if items.exists():
#         
            send_telegram_message(message)

from .models import CommunityPost, Comment

@receiver(post_save, sender=CommunityPost)
def notify_new_post(sender, instance, created, **kwargs):
    if created:
        title = instance.title
        author = instance.author.username
        post_type = instance.get_post_type_display()
        message = f"🗣️ منشور جديد في المجتمع: <b>{title}</b>\n👤 من طرف: <b>{author}</b>\n📌 النوع: <i>{post_type}</i>"
        send_telegram_message(message)

@receiver(post_save, sender=Comment)
def notify_new_comment(sender, instance, created, **kwargs):
    if created:
        author = instance.author.username
        post_title = instance.post.title
        content_preview = instance.content[:60]
        message = f"💬 تعليق جديد من <b>{author}</b> على المنشور <b>{post_title}</b>:\n<i>{content_preview}...</i>"
        send_telegram_message(message)
