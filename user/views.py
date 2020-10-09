import jwt
import bcrypt
import json

from django.views                    import View
from django.http                     import JsonResponse
from django.shortcuts                import redirect
from django.contrib.sites.shortcuts  import get_current_site 
from django.utils.http               import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail                import EmailMessage
from django.utils.encoding           import force_bytes, force_text

from .models            import User
from my_settings        import EMAIL
from .utils             import validate_email, validate_password
from .activation_token  import account_activation_token
from .text              import email_text


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
