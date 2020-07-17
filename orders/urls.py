from django.urls import path
from django.contrib import admin
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("menu", views.index, name="menu"),
    path("create/<int:productid>", views.create, name="create"),
    path("addtoorder/<int:productid>", views.addtoorder, name="addtoorder"),
    path("removefromorder/<int:itemid>", views.removefromorder, name="removefromorder"),
    path("confirm", views.confirm, name="confirm"),
    path("order/<int:orderid>", views.order, name="order"),
    path("orderhistory", views.orderhistory, name="orderhistory"),
    path("ordertickets", views.ordertickets, name="ordertickets"),
    path("ordertickets/<int:statusid>", views.ordertickets, name="ordertickets"),
    path("login", views.loginUser, name="login"),
    path("logout", views.logoutUser, name="logout"),
    path("register", views.registerUser, name="register")

]
