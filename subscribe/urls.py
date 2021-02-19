from django.urls import path
from . import views

urlpatterns = [
    path("subscription", views.subscription, name="subscription"),
    path('', views.redirect_subscribe, name="redirect_subscribe"),
]
