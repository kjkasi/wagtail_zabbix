from django.conf import settings
from django.db import models
from wagtail.models import Page


class PageSubscription(models.Model):
    """A user's active or historical interest in a Wagtail page."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_page_subscriptions",
    )
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="notification_page_subscriptions",
    )
    is_active = models.BooleanField(default=True)  # type: ignore[assignment]
    subscribed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "page"],
                name="unique_page_subscription",
            ),
        ]
        ordering = ["-updated_at"]

    def __str__(self):
        state = "active" if self.is_active else "inactive"
        return f"{self.user} → {self.page} ({state})"
