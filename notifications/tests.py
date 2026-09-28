from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from content.models import DemoPage
from home.models import HomePage
from notifications.models import PageSubscription
from wagtail.models import Page, PageViewRestriction, Site


class SubscriptionTests(TestCase):
    def setUp(self):
        root = Page.get_first_root_node()
        assert root is not None
        homepage = HomePage(title="Home")
        root.add_child(instance=homepage)
        self.demo_page = DemoPage(
            title="Release notes",
            intro="New features are published here.",
        )
        homepage.add_child(instance=self.demo_page)
        site = Site.objects.get(is_default_site=True)
        site.root_page = homepage  # type: ignore[assignment]
        site.save()  # type: ignore[call-arg]
        self.user = get_user_model().objects.create(username="subscriber")
        self.user.set_unusable_password()
        self.user.save(update_fields=["password"])  # type: ignore[call-arg]

    def test_page_is_rendered_with_subscribe_control(self):
        response = self.client.get(self.demo_page.url)

        self.assertEqual(response.status_code, 200)  # type: ignore[attr-defined]
        self.assertContains(response, "Sign in to subscribe")
        self.assertNotContains(response, "Subscribe to updates")

    def test_subscribe_requires_authentication(self):
        url = reverse("notifications:subscribe", args=[self.demo_page.pk])
        response = self.client.post(url)

        self.assertRedirects(
            response,
            f"/accounts/login/?next={url}",
        )
        self.assertFalse(PageSubscription.objects.exists())  # type: ignore[attr-defined]

    def test_authenticated_user_can_subscribe_once(self):
        self.client.force_login(self.user)
        url = reverse("notifications:subscribe", args=[self.demo_page.pk])

        first_response = self.client.post(url)
        second_response = self.client.post(url)

        self.assertRedirects(first_response, self.demo_page.url)
        self.assertRedirects(second_response, self.demo_page.url)
        self.assertEqual(
            PageSubscription.objects.filter(  # type: ignore[attr-defined]
                user=self.user,
                page=self.demo_page,
                is_active=True,
            ).count(),
            1,
        )
        self.assertContains(self.client.get(self.demo_page.url), "Unsubscribe")

    def test_unsubscribe_deactivates_without_deleting_history(self):
        subscription = PageSubscription.objects.create(  # type: ignore[attr-defined]
            user=self.user,
            page=self.demo_page,
        )
        self.demo_page.allow_subscriptions = False  # type: ignore[assignment]
        self.demo_page.save(update_fields=["allow_subscriptions"])  # type: ignore[call-arg]
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("notifications:unsubscribe", args=[self.demo_page.pk])
        )

        self.assertRedirects(response, self.demo_page.url)
        subscription.refresh_from_db()
        self.assertFalse(subscription.is_active)
        self.assertEqual(PageSubscription.objects.count(), 1)  # type: ignore[attr-defined]

    def test_subscription_is_not_allowed_for_restricted_page(self):
        restricted_group = Group.objects.create(name="restricted")
        restriction = PageViewRestriction.objects.create(  # type: ignore[attr-defined]
            page=self.demo_page,
            restriction_type=PageViewRestriction.GROUPS,
        )
        restriction.groups.add(restricted_group)  # type: ignore[attr-defined]
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("notifications:subscribe", args=[self.demo_page.pk])
        )

        self.assertEqual(response.status_code, 404)  # type: ignore[attr-defined]
        self.assertFalse(PageSubscription.objects.exists())  # type: ignore[attr-defined]

    def test_subscription_is_not_allowed_for_opted_out_page(self):
        self.demo_page.allow_subscriptions = False  # type: ignore[assignment]
        self.demo_page.save(update_fields=["allow_subscriptions"])  # type: ignore[call-arg]
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("notifications:subscribe", args=[self.demo_page.pk])
        )

        self.assertEqual(response.status_code, 404)  # type: ignore[attr-defined]
        self.assertFalse(PageSubscription.objects.exists())  # type: ignore[attr-defined]

    def test_authenticated_user_can_log_out_with_post(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("logout"))

        self.assertEqual(response.status_code, 200)  # type: ignore[attr-defined]
        self.assertNotIn("_auth_user_id", self.client.session)
