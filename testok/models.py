from django.db import models
from django.contrib.auth.hashers import make_password
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy

import random
import uuid
import datetime


#######################################################################################################################################
#PRODUCT MODELS
#######################################################################################################################################

class Category(models.Model):
    _id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name}'

class Brand(models.Model):
    _id = models.UUIDField(default=uuid.uuid4,editable=False, primary_key=True)
    name = models.CharField(max_length=256, blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True,editable=False)

    def get_absolute_url(self):
        return f'{self.name}'
    
    def __str__(self):
        return self.name

class Product(models.Model):
    _id = models.UUIDField(default=uuid.uuid4,editable=False, primary_key=True)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, null=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=256, blank=False, unique=True)
    price = models.DecimalField(default=0, blank=False, decimal_places=2, max_digits=10, validators=[MinValueValidator(0.0)])
    quantity = models.PositiveIntegerField(default=0, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, auto_now=True)
    deleted_at = models.DateTimeField(null=True,editable=False)

    def get_absolute_url(self):
        return f'{self.brand.name}/{self._id}'

    def __str__(self):
        return f'({self.brand.name}) {self.name}'

    class Meta:
        unique_together = ('brand', 'name',)

class ProductImage(models.Model):
    _id = models.UUIDField(default=uuid.uuid4,editable=False, primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    url = models.URLField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return f'{self.url}'


#######################################################################################################################################
#USER MODELS
#######################################################################################################################################



class User(models.Model):
    def validate_ktp(x):
        if len(x)!=16 or not x.isdigit():
            raise ValidationError(
                gettext_lazy(f"{x} is invalid for KTP."),
                params={"value": x},
            )

    def random_ktp():
        return str(random.randint(1111111111111111,9999999999999999))

    id_number = models.CharField(primary_key=True, validators=[validate_ktp], max_length=16, default=random_ktp)
    username = models.CharField(unique=True, max_length=50,)
    password = models.CharField(null=False, max_length=100)
    first_name = models.CharField(null=False, max_length=100)
    last_name = models.CharField(null=False, max_length=100)
    email = models.EmailField(unique=True, null=False)
    date_of_birth = models.DateField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super(User, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return f'{self.username}'

    def __str__(self):
        return f'{self.username}'

class UserAddress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    line_1 = models.CharField(max_length=252, null=False)
    line_2 = models.CharField(max_length=252, null=False)
    provinsi = models.CharField(max_length=20, null=False)
    kab_kota = models.CharField(max_length=50, null=False)
    kecamatan = models.CharField(max_length=50, null=False)
    kelurahan = models.CharField(max_length=50, null=False)
    zip_code = models.PositiveIntegerField(null=False)

    def __str__(self):
        return f'{self.User.username}'
    

#######################################################################################################################################
#TRANSACTION MODELS
#######################################################################################################################################

class Order(models.Model):
    _id = models.UUIDField(default=uuid.uuid4,editable=False, primary_key=True)
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False, null=False)
    is_delivered = models.BooleanField(default=False, null=False)
    is_cancelled = models.BooleanField(default=False, null=False)

    def get_absolute_url(self):
        return f'order/{self._id}'

    def __str__(self):
        return f'{" ".join([self.user.first_name, self.user.last_name])} {self.created_at}'
    

    
class OrderItem(models.Model):
    _id = models.UUIDField(default=uuid.uuid4,editable=False, primary_key=True)
    order = models.ForeignKey(Order, null=False, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=False, on_delete=models.CASCADE)
    product_quantity = models.IntegerField(validators=[MinValueValidator(1)])
    is_discount = models.BooleanField(default=False, null=False)
    discount = models.DecimalField(default=0.0, decimal_places=2, validators = [MinValueValidator(0.0), MaxValueValidator(1.0)], max_digits=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        unique_together = ('order', 'product',)

    def __str__(self):
        return f'{" ".join([self.order.user.first_name, self.order.user.last_name])} {self.order.created_at} {self.product.name}'


models_list = [
                ProductImage,
                Product,
                Brand,
                # User,
                OrderItem,
                Order
              ]