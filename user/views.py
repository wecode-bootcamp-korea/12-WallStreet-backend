import jwt
import bcrypt
import json
import uuid
import requests

from django.views                    import View
from django.http                     import JsonResponse
from django.shortcuts                import redirect
from django.contrib.sites.shortcuts  import get_current_site 
from django.utils.http               import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail                import EmailMessage
from django.utils.encoding           import force_bytes, force_text
from django.db.models                import Avg

from .models                import User, WishList, Asset
from order.models           import Order
from my_settings            import EMAIL
from wallstreet.settings    import SECRET_KEY, ALGORITHM
from .utils                 import validate_email, validate_password
from .activation_token      import account_activation_token
from .text                  import email_text
from utils                  import login_required


class SignUpView(View):
    def post(self, request):
        data = json.loads(request.body)

        try: 
            user_password = data['password']
            user_email    = data['email']

            if User.objects.filter(email=user_email).exists():
                return JsonResponse({'message':'DUPLICATED_REGISTER'}, status=400)

            if validate_email(user_email) or validate_password(user_password):
                return JsonResponse({'message':'INVALID_INFOS'}, status=400)

            password = bcrypt.hashpw(
                    user_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            user = User(
                    email    = user_email,
                    password = password, 
                    )
            user.save()

            current_site = get_current_site(request)
            domain       = current_site.domain
            uidb64       = urlsafe_base64_encode(force_bytes(user.id))
            token        = account_activation_token.make_token(user)
            message_data = email_text(domain, uidb64, token) 

            mail_title = '이메일 인증을 완료해주세요'
            email      = EmailMessage(mail_title, message_data, to=[user_email])
            email.send()

            return JsonResponse({'message':'SUCCESS'}, status=201)
        
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)

class ActivateView(View):
    def get(self, request, uidb64, token):
        try:
            uid  = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)

            if account_activation_token.check_token(user, token):
                user.is_active = True
                user.save()

                return redirect(EMAIL['REDIRECT_PAGE'])
            return JsonResponse({'message':'INVALID_TOKEN'}, stutus=400)

        except KeyError:
            return JsonResponse({'message':'INVALID_KEY'}, status=400)

class SocialSignInView(View):
    def post(self, request): 
        try:
            access_token = request.headers.get('Authorization')
            kakao_data = requests.get(
                    "https://kapi.kakao.com/v2/user/me", headers={"Authorization" : f"Bearer {access_token}"},
                ).json() 

            kakao_name  = kakao_data['kakao_account']['profile']['nickname']
            kakao_id    = kakao_data['id']
            kakao_email = kakao_name+str(kakao_id)      

            if not User.objects.filter(email=kakao_email).exists():
                User.objects.create(
                    name        = kakao_name,
                    nickname    = str(uuid.uuid4())[:8],
                    email       = kakao_name+str(kakao_id),
                    password    = bcrypt.hashpw(str(uuid.uuid4()).encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                )
                accessed_user   = User.objects.get(email=kakao_email)
                access_token    = jwt.encode({'user_id': accessed_user.id}, SECRET_KEY, ALGORITHM)
                return JsonResponse({'Authorization': access_token.decode('utf-8')}, status=200)        
            
            accessed_user   = User.objects.get(email=kakao_email)
            access_token    = jwt.encode({'user_id': accessed_user.id}, SECRET_KEY, ALGORITHM)
            return JsonResponse({'Authorization': access_token.decode('utf-8')}, status=200)

        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=401)

class SignInView(View):
    def post(self, request):           
        data = json.loads(request.body)
        try:
            if not User.objects.filter(email=data['email']):
                return JsonResponse({'message':'INVALID_USER'}, status=401)

            if not bcrypt.checkpw(
                    data['password'].encode('utf-8'), 
                    User.objects.get(email = data['email']).password.encode('utf-8')
                ):                
                return JsonResponse({'message':'INVALID_USER'}, status=401)

            accessed_user   = User.objects.get(email=data['email'])
            access_token = jwt.encode({'user_id': accessed_user.id}, SECRET_KEY, ALGORITHM)
            return JsonResponse({'Authorization': access_token.decode('utf-8')}, status=200)
            
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)
            
class WishListView(View):
    @login_required
    def post(self, request, *args, **kwars):
        data = json.loads(request.body)
        try:
            if WishList.objects.filter(user_id=request.user.id, product_id=data['product_id']).exists():
                WishList.objects.get(user_id=request.user.id, product_id=data['product_id']).delete()
                return JsonResponse({'message':"SUCCESS"}, status=200)

            WishList.objects.create(user_id=request.user.id, product_id=data['product_id'])
            return JsonResponse({'message':'SUCCESS'}, status=200)

        except:
            return JsonResponse({'message':'KEY_ERROR'}, status=401)

class AssetListView(View):
    @login_required
    def get(self, request):
        user = request.user
        try:
            existing_buy_orders = Order.objects.filter(
                user_id=user.id, 
                buy_or_sell=False, 
                status=True)
          
            pending_order_amount = sum([order.remaining_quantity*order.price for order in existing_buy_orders])
            user_asset           = Asset.objects.filter(user=user).select_related('user','product').prefetch_related('product__transaction_set')
            user_balance         = user.bank_account.balance
            available_balance    = user_balance - pending_order_amount
            coin_list            = [
                {
                "product_id"           : coin.product.id,
                "icon"                 : coin.product.image_url,
                "coin_name"            : coin.product.full_name,
                "coin_code"            : coin.product.abbreviation_name,
                "quantity"             : round(float(coin.product_quantity)),
                "available_coin"       : round(float(coin.product_quantity - sum([available_quantity.remaining_quantity \
                                                                    for available_quantity in coin.user.order_set\
                                                                    .filter(product_id=coin.product.id, buy_or_sell=True, status=True)]))),
                "average_buying_price" : coin.product.transaction_set.filter(buying_order__user_id=coin.user.id).aggregate(Avg('price')),
                "buying_price"         : round(float(coin.user.order_set.filter(buy_or_sell=False, product_id=coin.product.id).last().price)),                   
                "current_price"        : round(float(coin.product.transaction_set.last().price)),
                "profit_rate"          : round(float(((coin.product.transaction_set.last().price)/
                                        (coin.user.order_set.filter(buy_or_sell=False, product_id=coin.product.id).last().price)) * 100)-100
                                        )} for coin in user_asset if len(coin.product.transaction_set.filter(buying_order__user_id=coin.user.id)) > 0]
            
            coin_balance       = sum([coin['current_price'] * coin['quantity'] for coin in coin_list])
            total_buying_price = sum([coin['buying_price'] * coin['quantity'] for coin in coin_list])
            profit             = coin_balance - total_buying_price
            profit_rate        = ((coin_balance / total_buying_price) * 100) - 100
        
            return JsonResponse({'coin_list'       : coin_list, 
                                'total_asset'      : round(float(user_balance + coin_balance)),
                                'won_balance'      : round(float(user_balance)), 
                                'available_balance': round(float(available_balance)),
                                'coin_balance'     : round(float(coin_balance)),
                                'total_buy_price'  : round(float(total_buying_price)), 
                                'profit'           : round(float(profit)), 
                                'profit_rate'      : round(float(profit_rate),2)}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'message':'DOES_NOT_EXIST'}, status=400)
