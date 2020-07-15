import csv
from django.core.management.base import BaseCommand, CommandError
from orders.models import *
import decimal

def toCents(price):
    decimal.getcontext().prec = 2
    return decimal.Decimal(price)

def checkadd(objname, classname):
    if objname == '':
        return None
    else:
        try:
            obj = classname.objects.get(name=objname)
            print('obj exists: ' + objname)
            return obj
        except classname.DoesNotExist:
            o = classname(name=objname)
            o.save()
            print('obj added: ' + objname)
            return o

class Command(BaseCommand):
    help = 'Imports menu items'

    f = open("orders/management/data/menu_products.csv")
    productReader = csv.reader(f)
    next(productReader, None)  # skip the headers
    productData = list(productReader)

    ## import Products
    for productname, basename, variantname, sizename, price, includedtoppings in productData:

        if basename != '': # non-pizza products have no base
            productname = basename + ' ' + productname

        type = checkadd(productname, ProductType)
        variant = checkadd(variantname, Variant)
        size = checkadd(sizename, Size)
        type.availablevariants.add(variant)

        if includedtoppings != '':
            variant.includedtoppings = int(includedtoppings)
            variant.save()

        product = Product(type=type,variant=variant,size=size,price=toCents(price))

        try:
            product = Product.objects.get(type=type, variant=variant, size=size)
            print(f'product already exists: {productname} {variantname} {sizename}')
        except Product.DoesNotExist:
            product.save()

    f2 = open("orders/management/data/menu_toppings.csv")
    toppingReader = csv.reader(f2)
    next(toppingReader, None)  # skip the headers
    toppingData = list(toppingReader)

    ## import ToppingAddPrices and Toppings
    for toppingname, productname, variantname, sizename, addprice in toppingData:

        topping = checkadd(toppingname, Topping)
        producttype = checkadd(productname, ProductType)
        variant = checkadd(variantname, Variant)
        size = checkadd(sizename, Size)

        try:
            product = Product.objects.get(type=producttype, variant=variant, size=size)
            try:
                tap = ToppingAddPrice.objects.get(topping = topping, product=product)
                print(f'ToppingAddPrice already exists: {toppingname} on {productname} {variantname} {sizename}')
            except ToppingAddPrice.DoesNotExist:
                tap = ToppingAddPrice(topping = topping, product=product, addprice=toCents(addprice))
                tap.save()
                print('obj added: ToppingAddPrice ' + toppingname)
        except Product.DoesNotExist:
            print(f'topping not added: {toppingname} on {productname} {variantname} {sizename} - no such product exists.')


    statusnames = ["New","Paid","Accepted","Out for delivery","Delivered"]
    for statusname in statusnames:
        checkadd(statusname, Status)



    def handle(self, *args, **options):
        print('script is working')
        self.stdout.write('There are {} variants!'.format(Variant.objects.count()))
