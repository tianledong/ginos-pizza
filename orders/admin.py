from django.contrib import admin
from .models import *

admin.site.register(Topping)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(OrderProduct)
admin.site.register(Order)
admin.site.register(Additional)
admin.site.register(BillingAddress)
admin.site.register(Payment)
