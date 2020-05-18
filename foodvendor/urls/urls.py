from django.conf.urls import  url
from ..views import views
from ..views.vendor import SignUp, SetPassword , LoginUser
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token 

urlpatterns = [
    path('', views.index, name ='index'),
    path('api/v.1/vendor/signup', SignUp.as_view(), name = 'vendorsignup'),
    path('api/v.1/vendor/setpassword', SetPassword.as_view(), name = 'vendorsetpassword'),
    path('api/v.1/user/login', LoginUser.as_view(), name = 'userlogin'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]
