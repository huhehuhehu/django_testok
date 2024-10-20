from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth.hashers import check_password


from .models import *
from .serializer import *

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import json
import os
from PIL import Image
from io import BytesIO
import uuid

import firebase_admin
from firebase_admin import credentials, storage

cred = credentials.Certificate(os.path.join(os.getcwd(), 'serviceAccountKey.json'))
firebase_admin.initialize_app(cred, {
    'storageBucket': 'testok-9cd89.appspot.com'
})

if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred, {
        'storageBucket': '<your-firebase-storage-bucket>'
    })

bucket = storage.bucket()

class GetAll(APIView):
    def get(self, request, format=None):
        p = Product.objects.all()
        srl = ProductSerializer(p, many=True)
        return Response(srl.data)

class DeleteAll(APIView):
    def get(self, request, format=None):
        brands = Brand.objects.all().values_list('name', flat=True)

        try:
            for b in brands:
                for blob in bucket.list_blobs(prefix=f'{b}/'):
                    blob.delete()
        except:
            pass

        try:
            for m in models_list:
                m.objects.all().delete()
                return Response(status=status.HTTP_201_CREATED)

                
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):

    def get(self, request, brand_name, product_id, *args, **kwargs):
        product = get_object_or_404(Product, _id=product_id)
        srl = ProductSerializer(product)

        return Response(srl.data)

class GetUserDetails(APIView):

    def get(self, request):
        try:
            username = request.query_params.get('username')
            password = request.query_params.get('password')

            user=User.objects.get(username=username)

            if check_password(password, user.password):
                srl = UserSerializer(user)
                    
                return Response(srl.data)
                
            return Response({'status': 'error', 'message': 'Incorrect password!'}, status=status.HTTP_401_UNAUTHORIZED)
            

        except ObjectDoesNotExist:
            return Response({'status': 'error', 'message': 'Incorrect username!'}, status=status.HTTP_404_NOT_FOUND)


class OrderSummaryView(APIView):
    def get(self, request, order_id=None):
        try:
            if order_id:
                order = Order.objects.get(_id=order_id)  # Fetch the order by ID
                serializer = OrderSummarySerializer(order)
            else:
                order = Order.objects.all()  # Fetch the order by ID
                serializer = OrderSummarySerializer(order, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            retu

####################################################################################################################

@api_view(['POST'])
def insert_product(request):
    try:
        if isinstance(request.data, str):
            data = json.loads(request.data)
        else:
            data = request.data
        product = []

        brand_names = {i['brand'] for i in data}
        categories = {i['category'] for i in data}

        # existing_brands = set(Brand.objects.filter(name__in=brand_names).values_list('name', flat=True))
        # missing_brands = brand_names - existing_brands

        # existing_categories = set(Category.objects.filter(name__in=categories).values_list('name', flat=True))
        # missing_categories = categories - existing_categories

        for name in brand_names:
            Brand.objects.get_or_create(name=name)

        for name in categories:
            Category.objects.get_or_create(name=name)

        product = [
            Product(
                name=i['name'],
                brand = Brand.objects.get(name=i['brand']),
                category = Category.objects.get(name=i['category']),
                price=i['price'],
                quantity=i['quantity']
            ) for i in data
        ]

        Product.objects.bulk_create(product)
        
        return Response({
            'status': 'success',
            'message': 'Product inserted successfully',
            'total_inserted': len(data)
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def upload_product_image(request):
    def convert_to_png(image_path, output_path):
        img = Image.open(image_file)
    
        # Convert to 'RGBA' if necessary
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Create an in-memory file for the PNG
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Create a new InMemoryUploadedFile with PNG format
        return InMemoryUploadedFile(buffer, 'ImageField', image_file.name.split('.')[0] + '.png',
                                    'image/png', buffer.tell(), None)


    def upload_image_to_firebase(image, filename):


        blob = bucket.blob(filename)
        
        blob.upload_from_file(image)
        
        blob.make_public()
        
        return blob.public_url

    
    try:
        if 'image' not in request.FILES:
            return Response({
                'status': 'error',
                'message': 'No image file provided'
            }, status=status.HTTP_400_BAD_REQUEST)

        image = request.FILES['image']

        product = Product.objects.get(name=request.data['product'])
        brand = product.brand
        
        filename =  f'{uuid.uuid4()}'
        image_path = f'{brand.name}/{product._id}/{filename}.png'
        
        # Upload image to Firebase
        image_url = upload_image_to_firebase(image, image_path)
        
        # Save the ProductImage with the Firebase URL
        data = {
            'product': product._id,
            'url': image_url
        }
        serializer = ProductImageSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Image uploaded successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'status': 'error',
            'message': 'Invalid data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
