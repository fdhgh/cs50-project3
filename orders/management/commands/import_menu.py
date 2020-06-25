import csv
from django.core.management.base import BaseCommand, CommandError
from orders.models import *

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
    for productname, basename, variantname, sizename, price in productData:

        type = checkadd(productname, ProductType)
        variant = checkadd(variantname, Variant)
        size = checkadd(sizename, Size)
        type.availablevariants.add(variant)

        if basename == '': # products have no base
            product = Product(type=type,variant=variant,size=size,price=float(price))
        else:              # except pizza which has a base
            base = checkadd(basename,PizzaBase)
            product = Pizza(type=type,variant=variant,size=size,price=price,base=base)

        try:
            product = Product.objects.get(type=type, variant=variant, size=size)
            print(f'product already exists: {productname} {variantname} {sizename}')
        except Product.DoesNotExist:
            product.save()

    f2 = open("orders/management/data/menu_toppings.csv")
    toppingReader = csv.reader(f2)
    next(toppingReader, None)  # skip the headers
    toppingData = list(toppingReader)

    ## import Products
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
                tap = ToppingAddPrice(topping = topping, product=product, addprice=float(addprice))
                tap.save()
                print('obj added: ToppingAddPrice ' + toppingname)
        except Product.DoesNotExist:
            print(f'topping not added: {toppingname} on {productname} {variantname} {sizename} - no such product exists.')






    def handle(self, *args, **options):
        print('script is working')
        self.stdout.write('There are {} variants!'.format(Variant.objects.count()))
