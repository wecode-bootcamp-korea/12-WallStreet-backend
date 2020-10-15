from django.urls  import path
from .views       import SignUpView, ActivateView, SocialSignInView, WishListView, SignInView, AssetListView

urlpatterns = [
        path('/signup', SignUpView.as_view()), 
        path('/activate/<str:uidb64>/<str:token>', ActivateView.as_view()),
        path('/socialsignin', SocialSignInView.as_view()),
        path('/signin', SignInView.as_view()),
        path('/wishlists', WishListView.as_view()),
        path('/assets', AssetListView.as_view())
        ]
