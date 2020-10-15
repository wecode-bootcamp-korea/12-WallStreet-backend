from django.db import models

from user.models    import User
from product.models import Product

class Order(models.Model):
    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    product             = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity            = models.DecimalField(max_digits = 15, decimal_places = 4)
    price               = models.DecimalField(max_digits = 20, decimal_places = 4)
    remaining_quantity  = models.DecimalField(max_digits = 20, decimal_places = 4)
    ordered_at          = models.DateTimeField(auto_now_add=True)
    buy_or_sell         = models.BooleanField()
    status              = models.BooleanField(default=False)

    class Meta:
        db_table = 'orders'

class Transaction(models.Model):
    product         = models.ForeignKey(Product, on_delete=models.CASCADE)
    traded_at       = models.DateTimeField(auto_now=True)
    quantity        = models.DecimalField(max_digits = 15, decimal_places = 4)
    price           = models.DecimalField(max_digits = 20, decimal_places = 4)
    selling_order   = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='selling_transaction')
    buying_order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='buying_transaction')

    class Meta:
        db_table = 'transactions'

class Time_Unit(models.Model):
    name = models.IntegerField()

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'time_units'

class Report(models.Model):
    product             = models.ForeignKey(Product, on_delete=models.CASCADE)
    time_unit           = models.ForeignKey(Time_Unit, on_delete=models.CASCADE)
    opening_price       = models.DecimalField(max_digits = 20, decimal_places = 4)
    closing_price       = models.DecimalField(max_digits = 20, decimal_places = 4)
    high_price          = models.DecimalField(max_digits = 20, decimal_places = 4)
    low_price           = models.DecimalField(max_digits = 20, decimal_places = 4)
    transaction_volume  = models.DecimalField(max_digits = 20, decimal_places = 4)
    reported_time       = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reports'
