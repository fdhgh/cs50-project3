from django.db import models
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.

class Size(models.Model):
    name = models.CharField(max_length=16)

    def __str__(self):
        return f"{self.name}"

class Variant(models.Model): # fillings, right hand side of menu
    name = models.CharField(max_length=64, primary_key=True)
    includedtoppings = models.IntegerField(default=0)

class Topping(models.Model):
    name = models.CharField(max_length=64, primary_key=True)

class ProductType(models.Model):
    name = models.CharField(max_length=64, primary_key=True)
    availablevariants = models.ManyToManyField(Variant, blank=True, related_name="oftypes")
    availablesizes = models.ManyToManyField(Size, blank=True, related_name="oftypes")
    def listproducts(self):
        return Product.objects.filter(type = self).order_by('variant')
    productlist = property(listproducts)

class Product(models.Model):

    type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name="products")
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="products")

    class Meta:
       unique_together = ('type', 'variant')

    def getPriceList(self):
        pricelist=[]
        for s in self.type.availablesizes.all():
            try:
                psp = ProductSizePrice.objects.get(product=self,size=s)
                p=psp.price
            except ObjectDoesNotExist:
                p = ""
            pricelist.append(p)
        return pricelist

    pricelist = property(getPriceList)

    def listToppingAddPrice(self):
        return ToppingAddPrice.objects.filter(product=self)

    toppingaddpricelist = property(listToppingAddPrice)

    def __str__(self):
        return f"{self.type.name}: {self.variant.name}"

class ProductSizePrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sizeprices")
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name="prices")
    price = models.DecimalField(max_digits=10, decimal_places=2)


    class Meta:
       unique_together = ('product', 'price', "size")

class ToppingAddPrice(models.Model):
    topping = models.ForeignKey(Topping, on_delete=models.CASCADE, related_name="toppingprices")
    addprice = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="availabletoppings")

    class Meta:
       unique_together = ('topping', 'product')

class Item(models.Model):
    productsizeprice = models.ForeignKey(ProductSizePrice,on_delete=models.CASCADE, related_name="items")
    toppings = models.ManyToManyField(Topping, blank=True, related_name="items")
    price = models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return f"Item costs ${self.price}"


class Status(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

class Order(models.Model): # the latest order for the user represents the current Cart
    items = models.ManyToManyField(Item, blank=True, related_name="orders")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, blank=True, null=True, related_name="carts")
    status = models.ForeignKey(Status,on_delete=models.CASCADE, default=0, related_name="orders")
    datemodified = models.DateTimeField(auto_now=True)

    def calculateTotalPrice(self):
        total = 0
        for item in self.items.all():
            total += item.price
        return total

    totalPrice = property(calculateTotalPrice)

    def countItems(self):
        return self.items.count()
    itemscount = property(countItems)

    def __str__(self):
        return f"cart has {self.items.count()} items"

# class TicketsPermission(models.Model):
#
#     class Meta:
#
#         managed = False  # No database table creation or deletion  \
#                          # operations will be performed for this model.
#
#         default_permissions = () # disable "add", "change", "delete"
#                                  # and "view" default permissions
#
#         permissions = (
#             ('view_tickets', 'Can view order tickets for all customers'),
#         )
