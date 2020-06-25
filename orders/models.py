from django.db import models
from django.conf import settings

# Create your models here.


class Size(models.Model):
    name = models.CharField(max_length=16, primary_key=True)
    def __str__(self):
        return f"{self.id}. {self.name}"

class PizzaBase(models.Model):
    name = models.CharField(max_length=16, primary_key=True)

class Variant(models.Model): # fillings, right hand side of menu
    name = models.CharField(max_length=64, primary_key=True)

class Topping(models.Model):
    name = models.CharField(max_length=64, primary_key=True)

class ProductType(models.Model):
    name = models.CharField(max_length=64, primary_key=True)
    availablevariants = models.ManyToManyField(Variant, blank=True, related_name="oftypes")

class Product(models.Model):
    type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name="products")
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="products")
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name="items")
    price =  models.FloatField()

    class Meta:
       unique_together = ('type', 'variant', 'size', 'price')

class Pizza(Product):
    base = models.ForeignKey(PizzaBase, on_delete=models.CASCADE, related_name="pizzas",blank=True)#null=True because some menu items have no base

class ToppingAddPrice(models.Model):
    topping = models.ForeignKey(Topping, on_delete=models.CASCADE, related_name="toppingprices")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="availabletoppings")
    addprice = models.FloatField()

    class Meta:
       unique_together = ('topping', 'product')

class Item(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE, related_name="items")
    toppings = models.ManyToManyField(Topping, blank=True, related_name="items")

class Order(models.Model): # the latest order for the user represents the current Cart
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name="carts")
    items = models.ManyToManyField(Item, blank=True, related_name="orders")
