import json 

from django.views   import View 
from django.http    import JsonResponse

from utils          import login_required
from order.utils    import make_order, make_transaction
from user.models    import User, BankAccount, Asset
from product.models import Product
from .models        import Order, Transaction, Time_Unit, Report

def round_four(num):
    return float(round(num, 4))

class BuyTransactionView(View):
    @login_required
    def post(self,request):
        data = json.loads(request.body)
        user = request.user
      
        try:
            coin     = data['product_id']
            price    = float(data['price'])
            quantity = float(data['quantity'])
            
            if user.bank_account.balance > (price*quantity): # 자산이 코인 살 때 필요 금액보다 많고
                if Order.objects.filter(
                        user_id=user.id, 
                        buy_or_sell=False, 
                        status=True).exists():  # 동일 유저의 기존 매수 주문 존재 여부
                    existing_orders = Order.objects.filter(
                            user_id=user.id, 
                            buy_or_sell=False, 
                            status=True)
                    transaction_amount = sum([order.remaining_quantity*order.price for order in existing_orders]) # 기존 매수 주문 금액
                    
                    if transaction_amount < user.bank_account.balance: 
                        allowance = user.bank_account.balance - transaction_amount
                        allowed_quantity = allowance // price
                        quantity = min(quantity, allowed_quantity)
                        new_order = make_order(False, user, coin, quantity, price)
                        make_transaction(False, coin, price, new_order, user)
                        return JsonResponse({'message':'ORDER_CREATED'}, status=201)
                    return JsonResponse({'message':'INVALID_REQUEST'}, status=400)
                
                else: #기존 매수 없을 때 
                    new_order = make_order(False, user, coin, quantity, price)
                    make_transaction(False, coin, price, new_order, user)
                    return JsonResponse({'message':'SUCCESS'}, status=201)
            return JsonResponse({'message':'INVALID_REQUEST'}, status=400)

        except BankAccount.DoesNotExist:
            return JsonResponse({'message':'DOES_NOT_EXIST'}, status=400)
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)
        
    @login_required
    def patch(self,request, order_id):
        data = json.loads(request.body)
        
        try:
            quantity = float(data['quantity'])
            order    = Order.objects.get(id=order_id)
            
            if order.status == True and quantity < order.remaining_quantity:
                return JsonResponse({'message':'INVALID_REQUEST'}, status=400)
            
            elif order.status == True and quantity >= order.remaining_quantity:
                order.remaining_quantity = quantity - (order.quantity - order.remaining_quantity)
                order.quantity           = quantity
                order.price              = data['price']
                order.save()
                return JsonResponse({'message':'SUCCESS'}, status=200)

        except Order.DoesNotExist:
            return JsonResponse({'message':'DOES_NOT_EXIST'}, status=400)
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)

class SellTransactionView(View):
    @login_required
    def post(self,request):
        data = json.loads(request.body)
        user = request.user

        try:
            coin     = data['product_id']
            price    = float(data['price'])
            quantity = float(data['quantity'])

            if Asset.objects.filter(user_id=user.id,product_id=coin).exists(): # 팔려는 코인을 보유하고 있으면
                if Asset.objects.get(user_id=user.id, product_id=coin).product_quantity >= quantity: # 보유수량 >= 팔려는 수량
                    
                    new_order = make_order(True, user, coin, quantity, price)
                    make_transaction(True, coin, price, new_order, user)
                    
                    return JsonResponse({'message':'SOLD'}, status=201)
                return JsonResponse({'message':'INVALID_REQUEST'}, status=400)
            return JsonResponse({'message':'DOES_NOT_EXIST'}, status=400)
        
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)


class ReportListView(View):
    def get(self, request, product_id):
        reports     = Report.objects.filter(product_id=product_id, time_unit_id=1).order_by('reported_time')
        report_data = [
            {
                "opening_price"      : round_four(report.opening_price),
                "closing_price"      : round_four(report.closing_price),
                "high_price"         : round_four(report.high_price),
                "low_price"          : round_four(report.low_price),
                "transaction_volume" : round_four(report.transaction_volume),
                "reported_time"      : ((report.reported_time).timestamp() * 1000)
            } for report in reports]
        return JsonResponse({'report_data':report_data}, status=200)
