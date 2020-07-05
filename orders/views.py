from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from .models import *

# Create your views here.
def index(request):

    producttypes = ProductType.objects.all()

    context = {
        "producttypes": producttypes
        }

    return render(request, "orders/index.html", context)


def create(request, productid):

    product = Product.objects.get(id=productid)
    context = {
        "product": product,
        "toppings": ToppingAddPrice.objects.filter(product=product)
        }

    return render(request, "orders/create.html", context)


def addtoorder(request, productid):

    product = Product.objects.get(id=productid)
    price  = product.price
    toppings = request.POST.getlist('toppings')
    item = Item(product=product,price=price)     # ManyToManyField items can't be added to a model until after it's been saved. https://stackoverflow.com/a/18801489/13800944
    item.save()
    for t in toppings:
        print("topping id: " + str(t))
        tap = ToppingAddPrice.objects.get(id=t)
        print("topping name: " + str(tap.topping.name))
        price += tap.addprice
        item.toppings.add(tap.topping)
    item.price = price
    item.save()
    print("item saved")

    context = {
        "product": product,
        "toppings": ToppingAddPrice.objects.filter(product=product)
        }

    return render(request, "orders/create.html", context)
