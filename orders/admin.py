from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Size)
admin.site.register(PizzaBase)
admin.site.register(Variant)
admin.site.register(Topping)
admin.site.register(ProductType)
admin.site.register(Product)
admin.site.register(Status)
