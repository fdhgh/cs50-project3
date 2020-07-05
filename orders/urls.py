from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("menu", views.index, name="menu"),
    path("create/<int:productid>", views.create, name="create")
]
