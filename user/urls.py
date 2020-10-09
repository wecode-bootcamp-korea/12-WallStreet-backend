from django.urls  import path
from .views       import SignUpView, ActivateView

urlpatterns = [
        path('/signup', SignUpView.as_view()), 
        path('/activate/<str:uidb64>/<str:token>', ActivateView.as_view())
        ]
