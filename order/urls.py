from django.urls import path
from .views      import MyOrderView, OrderView, TransactionView

urlpatterns = [
        path('/<int:product_id>', OrderView.as_view()),
        path('/myorders', MyOrderView.as_view()), # ValueError: invalid literal for int() with base 10: 'myorders'
        path('/transactions/<int:product_id>', TransactionView.as_view()),
]