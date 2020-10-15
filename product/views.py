import json
import datetime

from django.http            import JsonResponse
from django.views           import View
from django.db.models       import Q, Prefetch, Max, Min, Sum

from .models                import Product
from utils                  import is_wishlist
from order.models           import Report, Time_Unit

def round_four(num):
    return float(round(num, 4))

class ProductListView(View):
    def get(self, request, *args, **kwargs):
        products = Product.objects.filter(
            Q(full_name='썬쓰') | Q(full_name='방탄코인쓰')
            ).select_related('market').prefetch_related('transaction_set')
        
        now = datetime.datetime.now()
        midnight = datetime.datetime(now.year, now.month, now.day)
            
        time_unit_id = Time_Unit.objects.get(name=1).id    

        product_list = [
            {
                'product_id'            : product.id,
                'image_url'             : product.image_url,
                'abbreviation_name'     : product.abbreviation_name,
                'full_name'             : product.full_name,
                'market'                : product.market.name,
                'high'                  : round_four(product.transaction_set.filter(traded_at__gte=midnight).aggregate(Max('price')).get('price__max')), 
                'low'                   : round_four(product.transaction_set.filter(traded_at__gte=midnight).aggregate(Min('price')).get('price__min')), 
                'today_opening_price'   : round_four(product.transaction_set.filter(traded_at__lt=midnight).latest('traded_at').price), 
                'today_volume'          : round_four(product.transaction_set.filter(traded_at__gte=midnight).aggregate(Sum('quantity')).get('quantity__sum')), 
                'traded_money'          : round_four(sum([trade.quantity*trade.price for trade in product.transaction_set.filter(traded_at__gte=midnight)])), 
                'price_now'             : round_four(product.transaction_set.filter(traded_at__gte=midnight).latest('traded_at').price),  
                'change'                : round_four(
                (   product.transaction_set.order_by('-traded_at').first().price \
                - product.transaction_set.order_by('-traded_at').exclude(price=product.transaction_set.order_by('-traded_at').first().price).first().price) 
                / product.transaction_set.order_by('-traded_at').first().price*100
                ),
                'change_price'          : round_four(
                (   product.transaction_set.order_by('-traded_at').first().price \
                - product.transaction_set.order_by('-traded_at').exclude(price=product.transaction_set.order_by('-traded_at').first().price).first().price)
                ),
                'is_wishlist'           : is_wishlist(request, product_id=product.id)
            } for product in products]
        
        return JsonResponse({'message':product_list}, status=200)