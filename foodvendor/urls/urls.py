from django.conf.urls import  url
from ..views import views
from ..views.vendor import SignUp, SetPassword, LoginUser, Menu, MenuDetail
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token 

urlpatterns = [
    path('', views.index, name ='index'),
    path('api/v.1/vendor/signup', SignUp.as_view(), name = 'vendorsignup'),
    path('api/v.1/vendor/setpassword', SetPassword.as_view(), name = 'vendorsetpassword'),
    path('api/v.1/user/login', LoginUser.as_view(), name = 'userlogin'),
    path('api/v.1/vendor/menu', Menu.as_view(), name = 'menu'),
    path('api/v.1/vendor/menu/<int:pk>', MenuDetail.as_view(), name = 'menudetail'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]
