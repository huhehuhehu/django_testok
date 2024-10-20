from rest_framework import serializers
from .models import *


class BrandSerializer(serializers.ModelSerializer):
    # _id = serializers.UUIDField(format='hex', read_only=True)

    class Meta:
        model = Brand
        fields = (
                '_id',
                'name',
                'created_at'
                )

        extra_kwargs = {
            'created_at': {'read_only': True},
        }

class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = ('name')

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('product', 'url',)
        extra_kwargs = {
            'product': {'write_only': True}
            }


class ProductSerializer(serializers.ModelSerializer):

    # _id = serializers.UUIDField(format='hex', read_only=True)
    brand = serializers.CharField(source='brand.name')
    images = ProductImageSerializer(many=True)
    category = serializers.CharField(source='category.name')
    extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            'deleted_at': {'read_only': True},
            'get_absolute_url': {'read_only': True},
        }

    class Meta:
        model = Product
        fields = (
            '_id',
            'category',
            'brand',
            'name',
            'price',
            'quantity',
            'images',
            'created_at',
            'updated_at',
            'deleted_at',
            'get_absolute_url' 
        )

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'date_of_birth',
            'first_name',
            'last_name',
            'id_number',
            'email',
            'created_at',
            'updated_at',
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'created_at': {'read_only':True},
            'updated_at': {'read_only':True},

        }

class ProductDetailSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='product.name')

    class Meta:
        model = OrderItem
        fields = (
                'product_name',
                'product_quantity',
                'discount',
                'total_price')

    def get_total_price(self, obj):
        # Calculate total price for the item
        price_per_product = obj.product.price  # Assuming product has a price field
        quantity = obj.product_quantity
        discount = obj.discount if obj.is_discount else 0

        # Calculate the discounted price
        total_price = (price_per_product * quantity) * (1 - discount)
        return round(total_price, 2)  # Round to 2 decimal places

class OrderSummarySerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(source='_id')  # Assuming _id is the order ID
    full_name = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
                'order_id',
                'full_name',
                'products',
                'total_price',
                'created_at'
                )

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def get_products(self, obj):
        # Get all order items related to this order
        order_items = obj.orderitem_set.all()  # Assuming related_name is default
        return ProductDetailSerializer(order_items, many=True).data

    def get_total_price(self, obj):
        total = sum(item.product.price * item.product_quantity * (1 - item.discount) for item in obj.orderitem_set.all())
        return round(total, 2)
