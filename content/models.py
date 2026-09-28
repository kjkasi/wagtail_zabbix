from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class DemoPage(Page):
    """A page that users can follow for publication notifications."""

    intro = RichTextField(blank=True)
    allow_subscriptions = models.BooleanField(default=True)  # type: ignore[assignment]

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("allow_subscriptions"),
    ]

    parent_page_types = ["home.HomePage", "content.DemoPage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["subscription"] = None
        if request.user.is_authenticated:
            from notifications.models import PageSubscription

            context["subscription"] = PageSubscription.objects.filter(  # type: ignore[attr-defined]
                user=request.user,
                page=self,
                is_active=True,
            ).first()
        return context
