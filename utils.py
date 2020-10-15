import jwt

from django.http                import JsonResponse

from wallstreet.settings     import SECRET_KEY, ALGORITHM
from user.models             import User

def login_required(func):
    def wrapper(self, request, *args, **kwargs):
        if not request.headers.get('Authorization'): 
            return JsonResponse({'message':'NO_TOKEN'}, status=403)
        token = request.headers['Authorization']

        try:
            decoded_token = jwt.decode(token, SECRET_KEY, ALGORITHM)
            request.user  = User.objects.get(id=decoded_token['user_id'])
                    
        except jwt.exceptions.DecodeError:
            return JsonResponse({'message':'INVALID_TOKEN'}, status=403)

        return func(self, request, *args, **kwargs) 
        
    return wrapper

def is_wishlist(request, product_id, *args, **kwargs):
    try:
        token = request.headers.get('Authorization')
        decoded_token = jwt.decode(token, SECRET_KEY, ALGORITHM)
        user_id = decoded_token['user_id']
        if WishList.objects.filter(user_id=user_id, product_id=product_id).exists():
            return True
        return False
    except:
        return False