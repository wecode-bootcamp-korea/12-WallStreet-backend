from django.urls import path, include

urlpatterns = [
        path('accounts', include('user.urls')),
        path('orders', include('order.urls'))
]
