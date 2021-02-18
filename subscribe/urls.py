from django.urls import path
from . import views

urlpatterns = [
    path("subscription", views.subscription, name="subscription"),
]
