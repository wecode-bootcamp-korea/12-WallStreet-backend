from decimal        import Decimal


from user.models    import User, BankAccount, Asset
from product.models import Product
from .models        import Order, Transaction

def make_order(buy_or_sell ,user, coin, quantity, price):
    new_order = Order.objects.create(
                    user_id             = user.id,
                    product_id          = coin,
                    quantity            = quantity,
                    remaining_quantity  = quantity,
                    price               = price,
                    buy_or_sell         = buy_or_sell
                    )
    return new_order

def make_transaction(buy_or_sell, product_id, price, new_order, user):
    if Order.objects.filter(
            product_id=product_id, 
            price=price, 
            buy_or_sell=not buy_or_sell, 
            status=True).exists(): # 주문 걸었는데 해당 코인에 반대 주문 수량이 있을 때 
        stored_orders = Order.objects.filter(
                product_id=product_id, 
                price=price, 
                buy_or_sell=not buy_or_sell, 
                status=True).prefetch_related('user__bank_account_set','product_set').order_by('ordered_at')
        # 거래 생성 =========================================================
        for stored_order in stored_orders:
            if new_order.remaining_quantity > 0: 
                order_count = stored_order.remaining_quantity 
                transaction_quantity = min(new_order.remaining_quantity, order_count) # 한 번에 거래 가능한 수량
                
                if buy_or_sell == False:
                    selling_order, buying_order = stored_order, new_order
                else:
                    selling_order, buying_order = new_order, stored_order 
                new_transaction = Transaction.objects.create(
                                    product_id    = stored_order.product_id, 
                                    quantity      = transaction_quantity,
                                    price         = stored_order.price,
                                    selling_order = selling_order,
                                    buying_order  = buying_order
                                    )
                # 주문 업데이트 ===============================================
                stored_order.remaining_quantity -= new_transaction.quantity
                new_order.remaining_quantity -= new_transaction.quantity
                stored_order.save()
                new_order.save()
                
                if selling_order.remaining_quantity == 0:
                    selling_order.status = False
                    selling_order.save()
                if buying_order.remaining_quantity == 0:
                    buying_order.status = False
                    buying_order.save()
                # 자산 업데이트 ======================================================
                if buy_or_sell == False:
                    seller      = stored_order.user.bank_account
                    seller_coin = Asset.objects.get(product_id=stored_order.product_id, user_id=stored_order.user_id)
                    buyer       = new_order.user.bank_account
                    buyer_coin  = Asset.objects.filter(product_id=new_order.product_id, user_id=new_order.user.id)
                else:
                    seller       = new_order.user.bank_account
                    seller_coin  = Asset.objects.get(product_id=new_order.product_id, user_id=new_order.user_id)
                    buyer        = stored_order.user.bank_account
                    buyer_coin   = Asset.objects.filter(product_id=stored_order.product_id, user_id=stored_order.user.id)

                seller.balance += new_transaction.quantity * new_transaction.price
                seller_coin.product_quantity -= new_transaction.quantity
                
                if seller_coin.product_quantity == 0:
                    seller_coin.delete()
                else:
                    seller_coin.save()
                seller.save()
                
                buyer.balance -= new_transaction.quantity * new_transaction.price
                buyer.save()

                if buyer_coin:
                    buyer_coin[0].product_quantity += new_transaction.quantity
                    buyer_coin[0].save()
                else:
                    Asset.objects.create(
                            user_id            = user.id,
                            product_id         = new_order.product_id,
                            product_quantity   = new_order.quantity
                            )
    else:
        pass 
