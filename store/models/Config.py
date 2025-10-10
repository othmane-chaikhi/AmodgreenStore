from django.db import models


class SiteConfig(models.Model):
    """Singleton configuration for site-wide settings like Telegram credentials."""

    telegram_bot_token = models.CharField(max_length=200, blank=True, default="")
    telegram_chat_id = models.CharField(max_length=100, blank=True, default="")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuration du site"
        verbose_name_plural = "Configuration du site"

    def __str__(self) -> str:
        return "Configuration du site"

    @classmethod
    def get_solo(cls) -> "SiteConfig":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


