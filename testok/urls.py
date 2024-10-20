from django.urls import path, include

from .views import *

urlpatterns = [
    path('get_all/', GetAll.as_view()),
    path('insert_product/', insert_product),
    path('delete_all/', DeleteAll.as_view()),
    path('products/<str:brand_name>/<uuid:product_id>/', ProductDetailView.as_view()),
    path('upload_img/', upload_product_image),
    path('get_user_details/', GetUserDetails.as_view()),
    path('all_orders/', OrderSummaryView.as_view()),
    path('get_order/<uuid:order_id>/', OrderSummaryView.as_view()),
]