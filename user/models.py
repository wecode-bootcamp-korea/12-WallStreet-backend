from django.db import models

class User(models.Model):
    name         = models.CharField(max_length=50)
    nickname     = models.CharField(max_length=50)
    email        = models.EmailField(max_length=300)
    password     = models.CharField(max_length=500)
    bank_account = models.ForeignKey('BankAccount', on_delete=models.CASCADE, null=True)
    is_active    = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email 

    class Meta:
        db_table = 'users'

class BankAccount(models.Model):
    account_number         = models.CharField(max_length=200)
    account_bank           = models.ForeignKey(
                                'Bank', 
                                on_delete=models.CASCADE,
                                related_name='account_bank')
    virtual_account_number = models.CharField(max_length=200)
    virtual_account_bank   = models.ForeignKey(
                                'Bank', 
                                on_delete=models.CASCADE,
                                related_name='virtual_account_bank')
    balance                = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return self.account_bank

    class Meta:
        db_table = 'bank_accounts'

class Bank(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'banks'

#class Asset(models.Model):
    #user = models.ForeignKey(User, on_delete=models.CASCADE)
    #product 
    #product_quantity = models.DecimalField(max_digits=10, decimal_places=4)


#class WishList(models.Model):
    #user   = models.ForeignKey(User, on_delete=models.CASCADE)
    #product = models.ForeignKey(Product, on_delete=models.CASCADE)


