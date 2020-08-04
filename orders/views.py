from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.views.decorators import staff_member_required
import decimal
from .models import *


def newCart(request):
    newstatus = Status.objects.get(name="New")
    cart = Order(status=newstatus)
    current_user = request.user
    if current_user.is_authenticated:
        cart.user = current_user
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

    productsizeprices = ProductSizePrice.objects.filter(product=product).all()
    cart = getCart(request)
    context = {
        "product": product,
        "cart": cart,
        "producttoppings": producttoppings,
        "pizzatoppings": pizzatoppings,
        "productsizeprices": productsizeprices,
        "messages": messages
        }

    return context

def getNextStatus(prevstatus):
    try:
        newstatus = Status.objects.get(id=(prevstatus.id+1))
        return newstatus
    except ObjectDoesNotExist:
        return None

# Create your views here.
def index(request):

    cart = getCart(request)
    producttypes = ProductType.objects.all()

    context = {
        "producttypes": producttypes,
        "cart": cart
        }

    return render(request, "orders/index.html", context)


def create(request, productid):
    product = Product.objects.get(id=productid)
    context = createContext(request, product, "")
    return render(request, "orders/create.html", context)


def addtoorder(request, productid):

    product = Product.objects.get(id=productid)
    toppings = request.POST.getlist('toppings')
    pspid = request.POST.get('sizeradio')
    productsizeprice = ProductSizePrice.objects.get(id=pspid)
    price=productsizeprice.price

    # try:
    #     item = Item.objects.filter(productsizeprice=productsizeprice,toppings=toppings).first()
    # except ObjectDoesNotExist:
    item = Item(productsizeprice=productsizeprice,price=price)     # ManyToManyField items can't be added to a model until after it's been saved. https://stackoverflow.com/a/18801489/13800944
    item.save()
    for t in toppings:
        tap = ToppingAddPrice.objects.get(id=t)
        price += tap.addprice
        item.toppings.add(tap.topping)
    item.price = price

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
        ptt = Topping.objects.get(name=pt)
        item.toppings.add(ptt)

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
        context = {
            "cart": cart
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
        context = {
            "cart": cart
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
        user = authenticate(username=username, password=password)
        if user is None:
            message = "Username or password is wrong. Please try again."
            context = {"message": message}
            return render(request, "registration/login.html", context)
        else:
            login(request, user)
            # add current cart to user
            addCartTo(request,user)
        return redirect(index)
    else:
        return render(request, "registration/login.html")

def logoutUser(request):
    logout(request)
    return redirect(index)

def orderhistory(request):
    current_user = request.user
    if current_user.is_authenticated:
        order_history = Order.objects.filter(user=current_user, items__isnull=False).distinct().order_by('-datemodified') #, items__isnull=False
        context = {"orders": order_history}
        print(order_history)
        return render(request, "orders/orderhistory.html", context)
    else:
        message = "Please log in or register to view your order history."
        context = {"message": message}
        return render(request, "registration/login.html", context)

@staff_member_required
def ordertickets(request, statusid=None):
    statuses = Status.objects.all()
    if statusid is not None:
        status = Status.objects.get(id=statusid)
        orders = Order.objects.filter(status=status).order_by('-datemodified')
        nextstatus = getNextStatus(status)
        context = {"orders": orders,
                    "statuses": statuses,
                    "currentstatus": status,
                    "nextstatus": nextstatus}
    else:
        context = {"statuses": statuses}
    return render(request, "orders/ordertickets.html", context)


@staff_member_required
def incrementstatus(request, orderid):
    order = Order.objects.get(id=orderid)
    prevstatus = order.status
    newstatus = getNextStatus(prevstatus)
    if newstatus is not None:
        order.status = newstatus
        order.save()
        return redirect('ordertickets',statusid=prevstatus.id)
    else:
        message = f"Order with ID {order.id} is at the final status {order.status.name}"
        context = {
            "message": message
        }
        return render(request, "orders/error.html", context)
