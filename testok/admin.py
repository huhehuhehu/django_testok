from django.contrib import admin
from .models import *

admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(ProductImage)

admin.site.register(User)
admin.site.register(UserAddress)

admin.site.register(Order)
admin.site.register(OrderItem)
