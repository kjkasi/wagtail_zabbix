from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from content.models import DemoPage
from notifications.models import PageSubscription


@require_POST
@login_required
def subscribe(request, page_id):
    page = get_object_or_404(
        DemoPage,
        pk=page_id,
        live=True,
        allow_subscriptions=True,
    )
    PageSubscription.objects.update_or_create(  # type: ignore[attr-defined]
        user=request.user,
        page=page,
        defaults={"is_active": True},
    )
    messages.success(request, f"You are now subscribed to {page.title}.")
    return redirect(page.url)


@require_POST
@login_required
def unsubscribe(request, page_id):
    page = get_object_or_404(
        DemoPage,
        pk=page_id,
        live=True,
        allow_subscriptions=True,
    )
    updated = PageSubscription.objects.filter(  # type: ignore[attr-defined]
        user=request.user,
        page=page,
        is_active=True,
    ).update(is_active=False)
    if updated:
        messages.success(request, f"You are no longer subscribed to {page.title}.")
    return redirect(page.url)
