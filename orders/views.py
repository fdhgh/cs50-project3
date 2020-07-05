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
