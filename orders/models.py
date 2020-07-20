from django.db import models
from django.conf import settings

# Create your models here.

class Size(models.Model):
    name = models.CharField(max_length=16, primary_key=True)
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

    def listproducts(self):
        return Product.objects.filter(type = self).order_by('variant','-size')

    def listsizes(self):
        sizelist = []
        for p in self.productlist:
            if p.size not in sizelist:
                sizelist.append(p.size)
        return sizelist

    productlist = property(listproducts)
    sizelist = property(listsizes)


class Product(models.Model):
    type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name="products")
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="products")
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name="products")
    price =  models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
       unique_together = ('type', 'variant', 'size', 'price')

    def listToppingAddPrice(self):
        return ToppingAddPrice.objects.filter(product=self)

    toppingaddpricelist = property(listToppingAddPrice)

    def __str__(self):
        return f"{self.size.name} {self.type.name}: {self.variant.name} - ${self.price}"

class ToppingAddPrice(models.Model):
    topping = models.ForeignKey(Topping, on_delete=models.CASCADE, related_name="toppingprices")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="availabletoppings")
    addprice = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
       unique_together = ('topping', 'product')

    def __str__(self):
        return f"here you go: {self.product.size.name}"

class Item(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE, related_name="items")
    toppings = models.ManyToManyField(Topping, blank=True, related_name="items")
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Item costs ${self.product.price}"

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
