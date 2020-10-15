from django.urls import path, include

urlpatterns = [
        path('accounts', include('user.urls')),
        path('products', include('product.urls')),
        path('orders', include('order.urls'))
]
