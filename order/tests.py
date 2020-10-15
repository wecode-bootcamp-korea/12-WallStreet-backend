import json
import bcrypt
import jwt
import datetime

from django.test     import TestCase, Client

from user.models         import User, Asset, BankAccount,Bank
from product.models      import Product, Market
from order.models        import Order, Transaction, Report, Time_Unit
from my_settings         import SECRET, ALGORITHM

class BuyTransactionTest(TestCase):
    def setUp(self):
        Bank.objects.create(
            id=1,
            name='NH농협'
        )
        BankAccount.objects.create(
            id                      = 1,
            account_number          = 111111111,
            account_bank_id         = 1,
            virtual_account_number  = 111111111,
            virtual_account_bank_id = 1,
            balance                 = 1000
        )
        BankAccount.objects.create(
            id                      = 2,
            account_bank_id         = 1,
            account_number          = 222222222,
            virtual_account_number  = 222222222,
            virtual_account_bank_id = 1,
            balance                 = 10000
        )
        User.objects.create(
            id              = 1,
            email           = 'test@mail.com',
            password        = '1234567aA!',
            bank_account_id = 1,
            )
        User.objects.create(
            id              = 2,
            email           = 'test1@mail.com',
            password        = '1234567aA!',
            bank_account_id = 2,
            )

        self.token = jwt.encode({'user_id' :User.objects.get(id=1).id}, SECRET['secret'], algorithm = ALGORITHM).decode('utf-8')
       
        Market.objects.create(
            id                   = 1,
            name                 = 'main',
            transaction_fee_rate = 0
        )
        Product.objects.create(
            id                = 1,
            abbreviation_name = 'BTCS',
            full_name         = '방탄코인쓰',
            image_url         = 'https://cdn.pixabay.com/photo/2018/08/30/12/24/bitcoin-3642042_960_720.png',
            market_id         = 1
        )
        Product.objects.create(
            id                = 2,
            abbreviation_name = 'SUNS',
            full_name         = '썬쓰',
            image_url         = 'https://cdn.pixabay.com/photo/2016/11/05/20/08/sunflower-1801284_960_720.png',
            market_id         = 1
        )
        Order.objects.create(
            id                 = 1,
            user_id            = 1,
            product_id         = 1,
            quantity           = 5,
            price              = 1000,
            remaining_quantity = 5,
            buy_or_sell        = 1
        )
        Order.objects.create(
            id                 = 2,
            user_id            = 2,
            product_id         = 1,
            quantity           = 5,
            price              = 1000,
            remaining_quantity = 5,
            buy_or_sell        = 0
        )
        Order.objects.create(
            id                 = 3,
            user_id            = 1,
            product_id         = 2,
            quantity           = 1,
            price              = 500,
            remaining_quantity = 1,
            buy_or_sell        = 0
        )
        Transaction.objects.create(
            product_id       = 1,
            quantity         = 5,
            price            = 1000,
            selling_order_id = 1,
            buying_order_id  = 2
        )
        Asset.objects.create(
            user_id          = 1,
            product_id       = 1,
            product_quantity = 10
        )

    def tearDown(self):
        User.objects.all().delete()
        Market.objects.all().delete()
        Product.objects.all().delete()
        Order.objects.all().delete()
        Transaction.objects.all().delete()
        Asset.objects.all().delete()
        Bank.objects.all().delete()
        BankAccount.objects.all().delete()
    
    def test_buytransaction_post_success(self):
        client = Client()
        header = {"HTTP_Authorization":self.token}

        order = {
            "price":100,
            "product_id":1,
            "quantity": 2
        }

        response = client.post('/orders/buy', json.dumps(order), **header, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'message':'SUCCESS'})
    
    def test_buytransaction_post_invalid_request(self):
        client = Client()
        header = {"HTTP_Authorization":self.token}

        order = {
            "price":10000,
            "product_id":1,
            "quantity":20
        }

        response = client.post('/orders/buy', json.dumps(order), **header, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message':'INVALID_REQUEST'})
    
    def test_buytransaction_post_fail(self):
        client = Client()
        header = {"HTTP_Authorization":self.token}

        order = {
            "price":10000,
            "product_id":4,
            "quantity":4
        }

        response = client.post('/orders/buy', json.dumps(order), **header, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message':'INVALID_REQUEST'})

class SellTransactionTest(TestCase):
    def setUp(self):
        Bank.objects.create(
            id=1,
            name='NH농협'
        )
        BankAccount.objects.create(
            id                      = 1,
            account_number          = 111111111,
            account_bank_id         = 1,
            virtual_account_number  = 111111111,
            virtual_account_bank_id = 1,
            balance                 = 1000
        )
        BankAccount.objects.create(
            id                      = 2,
            account_bank_id         = 1,
            account_number          = 222222222,
            virtual_account_number  = 222222222,
            virtual_account_bank_id = 1,
            balance                 = 10000
        )
        User.objects.create(
            id              = 1,
            email           = 'test@mail.com',
            password        = '1234567aA!',
            bank_account_id = 1,
            )
        User.objects.create(
            id              = 2,
            email           = 'test1@mail.com',
            password        = '1234567aA!',
            bank_account_id = 2,
            )

        self.token = jwt.encode({'user_id' :User.objects.get(id=1).id}, SECRET['secret'], algorithm = ALGORITHM).decode('utf-8')
       
        Market.objects.create(
            id                   = 1,
            name                 = 'main',
            transaction_fee_rate = 0
        )
        Product.objects.create(
            id                = 1,
            abbreviation_name = 'BTCS',
            full_name         = '방탄코인쓰',
            image_url         = 'https://cdn.pixabay.com/photo/2018/08/30/12/24/bitcoin-3642042_960_720.png',
            market_id         = 1
        )
        Product.objects.create(
            id                = 2,
            abbreviation_name = 'SUNS',
            full_name         = '썬쓰',
            image_url         = 'https://cdn.pixabay.com/photo/2016/11/05/20/08/sunflower-1801284_960_720.png',
            market_id         = 1
        )
        Order.objects.create(
            id                 = 1,
            user_id            = 1,
            product_id         = 1,
            quantity           = 5,
            price              = 1000,
            remaining_quantity = 5,
            buy_or_sell        = 1
        )
        Order.objects.create(
            id                 = 2,
            user_id            = 2,
            product_id         = 1,
            quantity           = 5,
            price              = 1000,
            remaining_quantity = 5,
            buy_or_sell        = 0
        )
        Order.objects.create(
            id                 = 3,
            user_id            = 1,
            product_id         = 2,
            quantity           = 1,
            price              = 500,
            remaining_quantity = 1,
            buy_or_sell        = 0
        )
        Transaction.objects.create(
            product_id       = 1,
            quantity         = 5,
            price            = 1000,
            selling_order_id = 1,
            buying_order_id  = 2
        )
        Asset.objects.create(
            user_id          = 1,
            product_id       = 1,
            product_quantity = 10
        )

    def tearDown(self):
        User.objects.all().delete()
        Market.objects.all().delete()
        Product.objects.all().delete()
        Order.objects.all().delete()
        Transaction.objects.all().delete()
        Asset.objects.all().delete()
        Bank.objects.all().delete()
        BankAccount.objects.all().delete()
    
    def test_selltransaction_post_success(self):
        client = Client()
        header = {"HTTP_Authorization":self.token}

        order = {
            "price":100,
            "product_id":1,
            "quantity": 2
        }

        response = client.post('/orders/sell', json.dumps(order), **header, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'message':'SOLD'})
    
    def test_selltransaction_post_invalid_request(self):
        client = Client()
        header = {"HTTP_Authorization":self.token}

        order = {

            "price":10000,
            "product_id":1,
            "quantity":20
        }

        response = client.post('/orders/sell', json.dumps(order), **header, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message':'INVALID_REQUEST'})
    
    def test_selltransaction_post_fail(self):
        client = Client()
        header = {"HTTP_Authorization":self.token}

        order = {
            "price":10000,
            "product_id":2,
            "quantity":4
        }

        response = client.post('/orders/sell', json.dumps(order), **header, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message':'DOES_NOT_EXIST'})

class ReportListTest(TestCase):
    def setUp(self):
        Market.objects.create(
            id                   = 1,
            name                 = 'main',
            transaction_fee_rate = 0
        )
        Product.objects.create(
            id                = 1,
            abbreviation_name = 'BTCS',
            full_name         = '방탄코인쓰',
            image_url         = 'https://cdn.pixabay.com/photo/2018/08/30/12/24/bitcoin-3642042_960_720.png',
            market_id         = 1
        )
        Time_Unit.objects.create(
            id   = 1,
            name = 1
        )
        Report.objects.create(
            id                 = 1,
            product_id         = 1, 
            time_unit_id       = 1, 
            opening_price      = 1000,
            closing_price      = 500,
            high_price         = 1500,
            low_price          = 500,
            transaction_volume = 38.74
        )
    
    def tearDown(self):
        Market.objects.all().delete()
        Product.objects.all().delete()
        Time_Unit.objects.all().delete()
        Report.objects.all().delete()
    
    def test_reportlist_get_success(self):
        client = Client()
        report = Report.objects.get(id=1)
        reported_time = report.reported_time.timestamp()*1000
        response = client.get('/orders/reports/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
    "report_data": [
        {
            "opening_price": 1000.0,
            "closing_price": 500.0,
            "high_price": 1500.0,
            "low_price": 500.0,
            "transaction_volume": 38.74,
            "reported_time": reported_time
        }]})
