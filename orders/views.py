from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import logout, login
import decimal
from .models import *


def newCart(request):
    newstatus = Status.objects.get(name="New")
    cart = Order(status=newstatus)
    cart.save()
    request.session['cart_id'] = cart.id
    return cart

def getCart(request):
    try:
        cartid = request.session['cart_id']
        cart = Order.objects.get(id=cartid)
        if cart.status.name != "New":
            cart = newCart(request)
    except KeyError:
        cart = newCart(request)
    return cart

def getAnyCart(request):
    try:
        cartid = request.session['cart_id']
        cart = Order.objects.get(id=cartid)
    except KeyError:
        cart = newCart(request)
    return cart

def getTotal(request, cart):
    total = decimal.Decimal(0)
    items = cart.items.all()
    for item in items:
        total += item.price
    return total

def addCartTo(request, user):
    cart = getAnyCart(request)
    cart.user = user
    cart.save()

def createContext(request, product, message):
    messages = [message]
    producttoppings = ToppingAddPrice.objects.filter(product=product)

    if product.variant.includedtoppings >0:
        pizzatoppings = Topping.objects.all()
        if product.variant.includedtoppings > 1:
            messages.append("Choose up to " + str(product.variant.includedtoppings) + " toppings")
        else:
            messages.append("Choose a topping")

    else:
        pizzatoppings = None

    cart = getCart(request)
    total = getTotal(request,cart)
    context = {
        "product": product,
        "cart": cart,
        "total": total,
        "producttoppings": producttoppings,
        "pizzatoppings": pizzatoppings,
        "messages": messages
        }

    return context

# Create your views here.
def index(request):

    cart = getCart(request)
    total = getTotal(request, cart)
    producttypes = ProductType.objects.all()

    context = {
        "producttypes": producttypes,
        "cart": cart,
        "total": total
        }

    return render(request, "orders/index.html", context)


def create(request, productid):
    product = Product.objects.get(id=productid)

    context = createContext(request, product, "")

    print(context)
    return render(request, "orders/create.html", context)


def addtoorder(request, productid):

    product = Product.objects.get(id=productid)
    price  = product.price
    toppings = request.POST.getlist('toppings')

    try:
        item = Item.objects.get(product=product,toppings=toppings,price=price)
    except ObjectDoesNotExist:
        item = Item(product=product,price=price)     # ManyToManyField items can't be added to a model until after it's been saved. https://stackoverflow.com/a/18801489/13800944
        item.save()
        for t in toppings:
            print("topping id: " + str(t))
            tap = ToppingAddPrice.objects.get(id=t)
            print("topping name: " + str(tap.topping.name))
            price += tap.addprice
            item.toppings.add(tap.topping)

    pizzatoppings = request.POST.getlist('pizzatoppings')
    if len(pizzatoppings) > product.variant.includedtoppings:
        message = "Too many toppings selected."
        context = createContext(request, product, message)
        return render(request, "orders/create.html", context)
    elif len(pizzatoppings) < product.variant.includedtoppings:
        message = "Not enough toppings selected."
        context = createContext(request, product, message)
        return render(request, "orders/create.html", context)

    for pt in pizzatoppings:
        print(pt)
        ptt = Topping.objects.get(name=pt)
        item.toppings.add(ptt)

    item.price = price
    item.save()

    cart = getCart(request)

    cart.items.add(item)

    return redirect(index)

def removefromorder(request,itemid):
    item = Item.objects.get(id=itemid)
    cart = getCart(request)
    cart.items.remove(item)

    return redirect(index)

def confirm(request):

    if request.user.is_authenticated:
        # Do something for authenticated users.
        cart = getAnyCart(request)
        total = getTotal(request,cart)
        context = {
            "cart": cart,
            "total": total
            }
        return render(request, "orders/confirm.html", context)
    else:
        # Do something for anonymous users.
        message = "Please log in or register before completing your order."
        context = {"message": message}
        return render(request, "registration/register.html", context)

def order(request, orderid):
    try:
        cart = Order.objects.get(id=orderid)
        paidStatus = Status.objects.get(name="Paid")
        cart.status=paidStatus
        cart.save()
        total = getTotal(request,cart)
        context = {
            "cart": cart,
            "total": total
            }
        return render(request, "orders/confirm.html", context)
    except ObjectDoesNotExist:
        message = f"Order with ID {orderid} does not exist."
        context = {
            "message": message
        }
        return render(request, "orders/error.html", context)

def registerUser(request):
    if request.method == "POST":
        regUsername = request.POST.get("regUsername")
        regEmail = request.POST.get("regEmail")
        regPassword = request.POST.get("regPassword")
        confirmPassword = request.POST.get("confirmPassword")
        
        if User.objects.filter(username=regUsername).exists():
            message = "Username already taken. Please try a different username."
            context = {"message": message}
            return render(request, "registration/register.html", context)
        elif regPassword != confirmPassword:
            message = "Passwords must match."
            context = {"message": message}
            return render(request, "registration/register.html", context)
        else:
            # add user
            user = User.objects.create_user(username=regUsername, email=regEmail, password=regPassword)
            # login
            login(request, user)
            # add current cart to user
            addCartTo(request,user)
            return redirect(index)
    else: # GET request
        return render(request, "registration/register.html")

def loginUser(request):
    if request.method == "POST":
        # get user credentials
        username = request.POST.get("loginUsername")
        password = request.POST.get("loginPassword")
        # authenticate
        try:
            user = authenticate(username=username, password=password)
        except NameError:
            message = "Username or password is wrong. Please try again."
            context = {"message": message}
            return render(request, "registration/login.html", context)
        login(request, user)
        # add current cart to user
        addCartTo(request,user)

        return redirect(index)
    else:
        return render(request, "registration/login.html")

def logoutUser(request):
    logout(request)
    return redirect(index)
