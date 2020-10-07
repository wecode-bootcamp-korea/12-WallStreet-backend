from django.db import models

class Market(models.Model):
    name                    = models.CharField(max_length = 50)
    transaction_fee_rate    = models.DecimalField(max_digits = 10, decimal_places = 2)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'markets'

class Product(models.Model):
    abbreviation_name   = models.CharField(max_length = 10)
    full_name           = models.CharField(max_length = 50)
    image_url           = models.URLField(max_length = 500)
    market              = models.ForeignKey(Market, on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name
    
    class Meta:
        db_table = 'products'