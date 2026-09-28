from notifications import views

from django.urls import path


app_name = "notifications"

urlpatterns = [
    path("<int:page_id>/subscribe/", views.subscribe, name="subscribe"),
    path("<int:page_id>/unsubscribe/", views.unsubscribe, name="unsubscribe"),
]
