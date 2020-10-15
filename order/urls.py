from django.urls   import path
from .views        import BuyTransactionView, SellTransactionView, ReportListView

urlpatterns = [
        path('/buy', BuyTransactionView.as_view()),
        path('/change/<int:order_id>', BuyTransactionView.as_view()),
        path('/sell', SellTransactionView.as_view()),
        path('/reports/<int:product_id>', ReportListView.as_view())
        ]

