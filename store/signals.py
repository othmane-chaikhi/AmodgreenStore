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