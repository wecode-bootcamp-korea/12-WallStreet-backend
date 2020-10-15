import json
import datetime

from django.shortcuts       import render
from django.http            import JsonResponse
from django.db.models       import Q, Prefetch
from django.views           import View

from user.models            import User, Asset, BankAccount, Bank
from order.models           import Order, Transaction, Time_Unit, Report
from product.models         import Product
from utils                  import is_user_id, login_required
from order.utils            import make_order, make_transaction


def round_four(num):
    return float(round(num, 4))

class MyOrderView(View):
    def get(self, request, *args, **kwargs):
        user_id = is_user_id(request)

        if user_id:
            user = User.objects.prefetch_related('order_set', 
                                        'order_set__product').get(id=user_id)

            remaining_orderset       = user.order_set.filter(status=1).order_by('ordered_at')

            remaining_orders = [
                {
                    'buy_or_sell'           : '매도' if order.buy_or_sell else '매수',
                    'price'                 : round_four(order.price),
                    'remaining_quantity'    : round_four(order.remaining_quantity),
                    'ordered_quantity'      : round_four(order.quantity),
                    'ordered_at'            : order.ordered_at,
                    'product'               : order.product.abbreviation_name,
                    'order_id'              : order.id,
                    'product_id'            : order.product.id
                } for order in remaining_orderset]

            tradeset = Transaction.objects.filter(
                        Q(selling_order__user_id=user_id) | Q(buying_order__user_id=user_id)
                    ).select_related('product', 'buying_order', 'selling_order').order_by('traded_at')

            traded_orders = [
                {
                    'buy_or_sell'       : '매수' if trade.buying_order.user.id == user_id else '매도',
                    'price'             : round_four(trade.price),
                    'traded_quantity'   : round_four(trade.quantity),
                    'traded_at'         : trade.traded_at,
                    'product'           : trade.product.abbreviation_name,
                    'product_id'        : trade.product.id
                } for trade in tradeset]

            return JsonResponse({'message': {'remaining_orders':remaining_orders, 'traded_orders':traded_orders}}, status=200)
        return JsonResponse({'message':'NO_DATA'}, status=200)

class OrderView(View):
    def get(self, request, product_id, *args, **kwargs):
        product = Product.objects.prefetch_related('order_set').get(id=product_id)
        orderset = product.order_set.filter(status=1)
        
        sell_orderset = orderset.filter(buy_or_sell=True)
        buy_orderset  = orderset.filter(buy_or_sell=False) 
 
        sell_dict = {'total_quantity':0}
        buy_dict = {'total_quantity':0}

        for order in sell_orderset:
            order_price = round_four(order.price)
            order_quantity = round_four(order.quantity)
            if not order_price in sell_dict:
                sell_dict[order_price] = order_quantity
            else:
                sell_dict[order_price] += order_quantity
            sell_dict['total_quantity'] += order_quantity
                
        for order in buy_orderset:
            order_price = round_four(order.price)
            order_quantity = round_four(order.quantity)
            if not order_price in buy_dict: 
                buy_dict[order_price] = order_quantity
            else:
                buy_dict[order_price] += order_quantity
            buy_dict['total_quantity'] += order_quantity

        return JsonResponse({'message':{'sell':sell_dict, 'buy':buy_dict}}, status=200)

class TransactionView(View):
    def get(self, request, product_id, *args, **kwargs):
        NUMBER_OF_TRANSACTION_TO_SHOW = 31
        time_unit_id = Time_Unit.objects.get(name=1).id

        product = Product.objects.prefetch_related('transaction_set', 'report_set').get(id=product_id)
        transactions = product.transaction_set.order_by('-traded_at')[:NUMBER_OF_TRANSACTION_TO_SHOW]

        opening_price = transactions[30].price

        data = [
            {'traded_time'  : trade.traded_at,
            'price'         : round_four(trade.price),
            'quantity'      : round_four(trade.quantity), 
            'color'         : 'red' if trade.price < opening_price else 'blue',
            } for trade in transactions[:30]]

        return JsonResponse({'message':data}, status=200)