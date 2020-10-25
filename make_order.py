import schedule
import time
import random
import datetime
import faker

import os
import django
import sys

import bcrypt
import jwt

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wallstreet.settings")
django.setup()

from django.db.models       import Q, Prefetch, Sum

from wallstreet.settings    import SECRET_KEY, ALGORITHM
from product.models import Product
from order.models   import Order, Transaction, Time_Unit, Report
from user.models    import User, Asset

def round_four(num):
    return float(round(num, 4))

class Scheduler():
    def make_order(self, coin):
        fake = faker.Faker()

        users = User.objects.all().select_related('bank_account').select_related('bank_account').prefetch_related('order_set')
        user = random.choice(users)
        access_token = jwt.encode({'user_id': user.id}, SECRET_KEY, ALGORITHM).decode('utf-8')
        
        ordered_time = datetime.datetime.now()

        #sell
        # 랜덤시간 생성
        product = Product.objects.prefetch_related('transaction_set', 'asset_set', 'order_set').get(full_name=coin)
        product_id = product.id
        if product.asset_set.filter(user_id=user.id).exists():
            coin_in_asset = product.asset_set.get(user_id=user.id).product_quantity
            coin_other_orders = product.order_set.filter(status=1, \
                                                    user_id=user.id, 
                                                    buy_or_sell=True, 
                                                    product_id=product_id
                                                    ).aggregate(Sum('quantity')).get('quantity__sum') # 유저가 동일 상품 판다고 내놓은 거래들의 수량 합
            last_buy_order_price = round_four(product.order_set.filter(buy_or_sell=False).latest('ordered_at').price)

            if not coin_other_orders:
                coin_other_orders = 1
                available_coin_to_sell = coin_in_asset-coin_other_orders       
                if available_coin_to_sell > 2:

                    fake_quantity_sell = fake.random_int(
                                        1, round(available_coin_to_sell)
                                        )/2 

                    fake_price_sell = round(last_buy_order_price*fake.random_int(97, 103)/100)
                    print(fake_price_sell, '############3바이바이바이')
                    print(product.id)
                    os.system(f'http POST localhost:8000/orders/sell Authorization:{access_token} user_id={user.id} product_id={product_id} quantity={fake_quantity_sell} price={fake_price_sell}')

        #buy
         # 유저가 사겠다고 줄 선 다른 거래들 양*가격 총 합
        other_orders_of_user_sum  = sum([order.price*order.quantity for order in user.order_set.filter(buy_or_sell=False, status=1)])
        last_sell_order_price = round_four(product.order_set.filter(buy_or_sell=True).latest('ordered_at').price)

        available_money = float(user.bank_account.balance - other_orders_of_user_sum)
        if available_money:
            fake_price_buy = round(last_sell_order_price*fake.random_int(97, 103)/100)

            if available_money//fake_price_buy > 2:
                fake_quantity_buy = (
                    fake.random_int(1, available_money//fake_price_buy)
                    )/2 -fake.random_int(1,10)/100

                os.system(f'http POST localhost:8000/orders/buy Authorization:{access_token} product_id={product_id} quantity={fake_quantity_buy} price={fake_price_buy}')

    def report_maker(self, coin):
        now                     = datetime.datetime.now() 
        time                    = now - datetime.timedelta(0, 60) 
        report_start_time       = datetime.datetime(time.year, time.month, time.day, time.hour, time.minute)
        report_end_time         = report_start_time + datetime.timedelta(0, 60) 
        time_unit_id            = Time_Unit.objects.get(name=1).id

        product = Product.objects.prefetch_related('transaction_set').get(full_name=coin)
        last_closing_price      = product.transaction_set.filter(traded_at__lt=report_start_time).latest('traded_at').price

        transactions_to_report  = product.transaction_set.filter(
                                    traded_at__gte  = report_start_time,
                                    traded_at__lt   = report_end_time, 
                                ).order_by('traded_at')

        if len(transactions_to_report)==0:
            Report.objects.create(
            product_id          = product.id,
            time_unit_id        = time_unit_id, 
            opening_price       = last_closing_price,
            closing_price       = last_closing_price,
            high_price          = last_closing_price,
            low_price           = last_closing_price,
            transaction_volume  = 0,
            reported_time       = report_start_time,
            )

        else:
            transaction_price_list      = [trade.price for trade in transactions_to_report]
            transaction_quantity_list   = [trade.quantity for trade in transactions_to_report]

            Report.objects.create(
                product_id          = product.id,
                time_unit_id        = time_unit_id, 
                opening_price       = last_closing_price,
                closing_price       = transactions_to_report.last().price,
                high_price          = max(transaction_price_list), 
                low_price           = min(transaction_price_list), 
                transaction_volume  = sum(transaction_quantity_list),
                reported_time       = report_start_time,
                )

    def scheule_a_job(self, type="Secs", interval=1):

        if (type == "Secs"):
            schedule.every(interval).seconds.do(self.make_order, coin='썬쓰')
            schedule.every(interval).seconds.do(self.make_order, coin='방탄코인쓰')
            schedule.every(interval).seconds.do(self.make_order, coin='썬쓰')
            schedule.every(interval).seconds.do(self.make_order, coin='방탄코인쓰')
            schedule.every(interval).seconds.do(self.make_order, coin='썬쓰')
            schedule.every(interval).seconds.do(self.make_order, coin='방탄코인쓰')

        while True:
            schedule.run_pending()
            time.sleep(1)

    def schedule_a_job_2(self, type="Mins", interval=1):

        if (type == "Mins"):
            schedule.every(interval).minutes.do(self.report_maker, coin='썬쓰')
            schedule.every(interval).minutes.do(self.report_maker, coin='방탄코인쓰')

        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    run = Scheduler()
    run.scheule_a_job()
    run.schedule_a_job_2()