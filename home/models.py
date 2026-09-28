from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class HomePage(Page):
    """Landing page for the Wagtail + Zabbix prototype."""

    intro = RichTextField(
        default=(
            "This prototype demonstrates page subscriptions and notifications "
            "between Wagtail and Zabbix."
        )
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    max_count = 1
    subpage_types = ["content.DemoPage"]
