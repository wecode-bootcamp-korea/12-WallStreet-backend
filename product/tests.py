import datetime
import json
import bcrypt
import jwt

from django.test import TestCase, Client

from wallstreet.settings    import SECRET_KEY, ALGORITHM
from utils                  import is_wishlist
from user.models            import User, WishList, BankAccount, Bank, Asset
from order.models           import Order, Transaction, Report, Time_Unit
from .models                import Product, Market

class ProductListTest(TestCase):
    def setUp(self):
        
        Market.objects.create(name = 'Growth', transaction_fee_rate=0.02)
        market_id= Market.objects.get(name='Growth').id

        Product.objects.create(
            abbreviation_name  = 'SUNS',
            full_name          = '썬쓰',
            image_url          = 'https://cdn.pixabay.com/photo/2016/11/05/20/08/sunflower-1801284_960_720.png',
            market_id          = market_id,
        )
        Product.objects.create(
            abbreviation_name  = 'BTCS',
            full_name          = '방탄코인쓰',
            image_url          = 'https://cdn.pixabay.com/photo/2016/11/05/20/08/sunflower-1801284_960_720.png',
            market_id          = market_id,
        )
        suns_id = Product.objects.get(full_name='썬쓰').id
        btcs_id = Product.objects.get(full_name='방탄코인쓰').id

        Bank.objects.create(name='Test_Bank')
        bank_id = Bank.objects.get(name='Test_Bank').id

        # User Corine
        # User Corine makes 3 sell orders SUNS / 3 buy orders BTC
        BankAccount.objects.create(
            account_number          = 123123123,
            account_bank_id         = bank_id,            
            virtual_account_number  = 321321321,
            virtual_account_bank_id = bank_id,
            balance                 = 10000000,
        )

        corine_bank_account_id = BankAccount.objects.get(account_number=123123123).id

        User.objects.create(
            name                = 'Corine',
            email               = 'Corine@wecode.com',
            password            = bcrypt.hashpw("test_password".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            nickname            = 'nicknick',
            bank_account_id     = corine_bank_account_id,
        )
        corine_id = User.objects.get(email='Corine@wecode.com').id
        WishList.objects.create(user_id=corine_id, product_id=suns_id)

        Asset.objects.create(
            user_id          = corine_id,
            product_id       = suns_id,
            product_quantity = 50
        )

        Asset.objects.create(
            user_id          = corine_id,
            product_id       = btcs_id,
            product_quantity = 50
        )

        # Corine 3 sell orders SUNS / 3 buy orders BTC
        now = datetime.datetime(2020, 10, 12, 15, 10, 27, 852946)
        midnight = datetime.datetime(now.year, now.month, now.day)
        yesterday = midnight - datetime.timedelta(0,1)

        Order.objects.create(
            user_id             = corine_id,
            product_id          = suns_id,
            quantity            = 10,
            price               = 1000,
            remaining_quantity  = 1,
            ordered_at          = midnight,
            buy_or_sell         = True,
            status              = True,
        )

        Order.objects.create(
            user_id             = corine_id,
            product_id          = suns_id,
            quantity            = 15,
            price               = 1500,
            remaining_quantity  = 2,
            ordered_at          = midnight,
            buy_or_sell         = True,
            status              = True,
        )

        Order.objects.create(
            user_id             = corine_id,
            product_id          = suns_id,
            quantity            = 20,
            price               = 2000,
            remaining_quantity  = 0,
            ordered_at          = midnight,
            buy_or_sell         = True,
            status              = False,
        )

        Order.objects.create(
            user_id             = corine_id,
            product_id          = suns_id,
            quantity            = 1,
            price               = 77,
            remaining_quantity  = 0,
            ordered_at          = yesterday,
            buy_or_sell         = True,
            status              = False,
        )

        # Corine 3 buy orders BTC

        Order.objects.create(
            user_id             = corine_id,
            product_id          = btcs_id,
            quantity            = 100,
            price               = 100,
            remaining_quantity  = 0,
            ordered_at          = midnight,
            buy_or_sell         = False,
            status              = False,
        )

        Order.objects.create(
            user_id             = corine_id,
            product_id          = btcs_id,
            quantity            = 150,
            price               = 150,
            remaining_quantity  = 0,
            ordered_at          = midnight,
            buy_or_sell         = False,
            status              = False,
        )

        Order.objects.create(
            user_id             = corine_id,
            product_id          = btcs_id,
            quantity            = 200,
            price               = 200,
            remaining_quantity  = 20,
            ordered_at          = midnight,
            buy_or_sell         = False,
            status              = True,
        )
        
        Order.objects.create(
            user_id             = corine_id,
            product_id          = btcs_id,
            quantity            = 1,
            price               = 88,
            remaining_quantity  = 0,
            ordered_at          = yesterday,
            buy_or_sell         = False,
            status              = True,
        )
        # User_Soo
        # User Soo makes 3 buy orders SUNS / 3 sell orders BTC
        BankAccount.objects.create(
            account_number          = 19950104,
            account_bank_id         = bank_id,            
            virtual_account_number  = 321321321,
            virtual_account_bank_id = bank_id,
            balance                 = 10000000,
        )

        soo_bank_account_id = BankAccount.objects.get(account_number=19950104).id

        User.objects.create(
            name                = 'Soo',
            email               = 'Soo@wecode.com',
            password            = bcrypt.hashpw("test_password".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            nickname            = 'soonick',
            bank_account_id     = soo_bank_account_id,
        )
        soo_id = User.objects.get(email='Soo@wecode.com').id
        
        Asset.objects.create(
            user_id          = soo_id,
            product_id       = suns_id,
            product_quantity = 50
        )

        Asset.objects.create(
            user_id          = soo_id,
            product_id       = btcs_id,
            product_quantity = 50
        )

        # User Soo makes 3 buy orders SUNS 
        Order.objects.create(
            user_id             = soo_id,
            product_id          = suns_id,
            quantity            = 9,
            price               = 1000,
            remaining_quantity  = 0,
            ordered_at          = midnight,
            buy_or_sell         = False,
            status              = False,
        )

        Order.objects.create(
            user_id             = soo_id,
            product_id          = suns_id,
            quantity            = 13,
            price               = 1500,
            remaining_quantity  = 0,
            ordered_at          = midnight,
            buy_or_sell         = False,
            status              = False,
        )
        
        Order.objects.create(
            user_id             = soo_id,
            product_id          = suns_id,
            quantity            = 21,
            price               = 2000,
            remaining_quantity  = 1,
            ordered_at          = midnight,
            buy_or_sell         = False,
            status              = True,
        )

        Order.objects.create(
            user_id             = soo_id,
            product_id          = suns_id,
            quantity            = 1,
            price               = 77,
            remaining_quantity  = 0,
            ordered_at          = yesterday,
            buy_or_sell         = False,
            status              = True,
        )

        # User Soo 3 sells orders BTC
        Order.objects.create(
            user_id             = soo_id,
            product_id          = btcs_id,
            quantity            = 110,
            price               = 100,
            remaining_quantity  = 10,
            ordered_at          = midnight,
            buy_or_sell         = True,
            status              = True,
        )

        Order.objects.create(
            user_id             = soo_id,
            product_id          = btcs_id,
            quantity            = 145,
            price               = 150,
            remaining_quantity  = 5,
            ordered_at          = midnight,
            buy_or_sell         = True,
            status              = True,
        )

        Order.objects.create(
            user_id             = soo_id,
            product_id          = btcs_id,
            quantity            = 180,
            price               = 200,
            remaining_quantity  = 0,
            ordered_at          = midnight,
            buy_or_sell         = True,
            status              = False,
        )
        
        Order.objects.create(
            user_id             = soo_id,
            product_id          = btcs_id,
            quantity            = 1,
            price               = 88,
            remaining_quantity  = 0,
            ordered_at          = yesterday,
            buy_or_sell         = True,
            status              = False,
        )

        Transaction.objects.create(
            product_id          = suns_id,
            traded_at           = midnight+datetime.timedelta(0,2),
            quantity            = 9,
            price               = 1000,
            selling_order_id    = Order.objects.get(user_id=corine_id, price=1000).id,
            buying_order_id     = Order.objects.get(user_id=soo_id, price=1000).id,
        )

        Transaction.objects.create(
            product_id          = suns_id,
            traded_at           = midnight+datetime.timedelta(0,3),
            quantity            = 13,
            price               = 1500,
            selling_order_id    = Order.objects.get(user_id=corine_id, price=1500).id,
            buying_order_id     = Order.objects.get(user_id=soo_id, price=1500).id,
        )

        Transaction.objects.create(
            product_id          = suns_id,
            traded_at           = midnight+datetime.timedelta(0,1),
            quantity            = 20,
            price               = 2000,
            selling_order_id    = Order.objects.get(user_id=corine_id, price=2000).id,
            buying_order_id     = Order.objects.get(user_id=soo_id, price=2000).id,
        )

        Transaction.objects.create(
            product_id          = suns_id,
            traded_at           = yesterday,
            quantity            = 1,
            price               = 77,
            selling_order_id    = Order.objects.get(user_id=corine_id, price=77).id,
            buying_order_id     = Order.objects.get(user_id=soo_id, price=77).id,
        )

        # makes transactions for BTCS - Corine buys Soo sells
        Transaction.objects.create(
            product_id          = btcs_id,
            traded_at           = midnight+datetime.timedelta(0,4),
            quantity            = 100,
            price               = 100,
            selling_order_id    = Order.objects.get(user_id=soo_id, price=100).id,
            buying_order_id     = Order.objects.get(user_id=corine_id, price=100).id,
        )

        Transaction.objects.create(
            product_id          = btcs_id,
            traded_at           = midnight+datetime.timedelta(0,6),
            quantity            = 145,
            price               = 150,
            selling_order_id    = Order.objects.get(user_id=soo_id, price=150).id,
            buying_order_id     = Order.objects.get(user_id=corine_id, price=150).id,
        )

        Transaction.objects.create(
            product_id          = btcs_id,
            traded_at           = midnight+datetime.timedelta(0,5),
            quantity            = 180,
            price               = 200,
            selling_order_id    = Order.objects.get(user_id=soo_id, price=200).id,
            buying_order_id     = Order.objects.get(user_id=corine_id, price=200).id,
        )

        Transaction.objects.create(
            product_id          = btcs_id,
            traded_at           = yesterday,
            quantity            = 1,
            price               = 88,
            selling_order_id    = Order.objects.get(user_id=soo_id, price=88).id,
            buying_order_id     = Order.objects.get(user_id=corine_id, price=88).id,
        )

        # makes report for SUNS
        Time_Unit.objects.create(name=1)
        time_unit_id = Time_Unit.objects.get(name=1).id

        Report.objects.create(
            product_id          = suns_id,                     
            time_unit_id        = time_unit_id,
            opening_price       = 500,
            closing_price       = 50000,
            high_price          = 500000,
            low_price           = 50,
            transaction_volume  = 5,
            reported_time       = midnight,
        )

        # makes report for BTCS
        Report.objects.create(
            product_id          = btcs_id,                     
            time_unit_id        = time_unit_id,
            opening_price       = 700,
            closing_price       = 70000,
            high_price          = 700000,
            low_price           = 70,
            transaction_volume  = 7,
            reported_time       = midnight,
        )

    def tearDown(self):
        User.objects.all().delete()
        Market.objects.all().delete()
        Product.objects.all().delete()
        WishList.objects.all().delete()
        Order.objects.all().delete()
        Transaction.objects.all().delete()
        Report.objects.all().delete() 
        Time_Unit.objects.all().delete()

    def test_get_products_list_success_undefined_user(self):
        client = Client()
        response        = self.client.get(
                            '/products', 
                            content_type='application/json',
                            **{'HTTP_Authorization':'xxxx',
                            } 
                        )

        suns_id = Product.objects.get(full_name='썬쓰').id
        btcs_id = Product.objects.get(full_name='방탄코인쓰').id
        def round_four(num):
            return float(round(num, 4))
        
        self.maxDiff = None
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 
            {
            'message': [
            {
                'product_id': suns_id, 
                'image_url': 'https://cdn.pixabay.com/photo/2016/11/05/20/08/sunflower-1801284_960_720.png', 
                'abbreviation_name': 'SUNS',
                'full_name': '썬쓰', 
                'market': 'Growth',
                'high': round_four(2000), 
                'low': round_four(1000),
                'today_opening_price': round_four(500), 
                'today_volume': round_four(9+13+20),
                'traded_money': round_four(1000*9+1500*13+2000*20), 
                'price_now': round_four(1500), 
                'change': round_four((1500-1000)/1500*100), 
                'change_price': round_four(1500-1000), 
                'is_wishlist': False
            }, 
            {
                'product_id': btcs_id, 
                'image_url': 'https://cdn.pixabay.com/photo/2016/11/05/20/08/sunflower-1801284_960_720.png', 
                'abbreviation_name': 'BTCS', 
                'full_name': '방탄코인쓰', 
                'market': 'Growth', 
                'high': round_four(200), 
                'low': round_four(100), 
                'today_opening_price': round_four(700), 
                'today_volume': round_four(100+145+180), 
                'traded_money': round_four(100*100+150*145+200*180), 
                'price_now': round_four(150), 
                'change': round_four((150-200)/150*100), 
                'change_price': round_four(150-200), 
                'is_wishlist': False
            }]
            }
        )

    def test_get_products_list_success_corine(self):
        client = Client()

        corine_id       = User.objects.get(email='Corine@wecode.com').id
        access_token    = jwt.encode({'user_id': corine_id}, SECRET_KEY, ALGORITHM).decode('utf-8')
        response        = self.client.get(
                            '/products', 
                            content_type='application/json',
                            **{'HTTP_Authorization':access_token,
                            } 
                        )

        suns_id = Product.objects.get(full_name='썬쓰').id
        btcs_id = Product.objects.get(full_name='방탄코인쓰').id
        
        def round_four(num):
            return float(round(num, 4))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 
            {
            'message': [
            {
                'product_id': suns_id, 
                'image_url': 'https://cdn.pixabay.com/photo/2016/11/05/20/08/sunflower-1801284_960_720.png', 
                'abbreviation_name': 'SUNS',
                'full_name': '썬쓰', 
                'market': 'Growth',
                'high': round_four(2000), 
                'low': round_four(1000),
                'today_opening_price': round_four(500), 
                'today_volume': round_four(9+13+20),
                'traded_money': round_four(1000*9+1500*13+2000*20), 
                'price_now': round_four(1500), 
                'change': round_four((1500-1000)/1500*100), 
                'change_price': round_four(1500-1000), 
                'is_wishlist': True
            }, 
            {
                'product_id': btcs_id, 
                'image_url': 'https://cdn.pixabay.com/photo/2016/11/05/20/08/sunflower-1801284_960_720.png', 
                'abbreviation_name': 'BTCS', 
                'full_name': '방탄코인쓰', 
                'market': 'Growth', 
                'high': round_four(200), 
                'low': round_four(100), 
                'today_opening_price': round_four(700), 
                'today_volume': round_four(100+145+180), 
                'traded_money': round_four(100*100+150*145+200*180), 
                'price_now': round_four(150), 
                'change': round_four((150-200)/150*100), 
                'change_price': round_four(150-200), 
                'is_wishlist': False
            }]
            }
        )