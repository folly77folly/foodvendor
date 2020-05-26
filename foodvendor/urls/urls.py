from django.conf.urls import  url
from ..views import views
from ..views.vendor import VendorSignUp, Menu, MenuDetail, OrderStatus, VendorOrderDetail, VendorSales, MessageStatus, VendorSendBalances,OrderHistory, OrdersStatus
from ..views.customer import SignUp,  Order, CustomerOrderDetail, AllMenu, OrdersHistory, CancelOrder, VendorAllMenu
from ..views.auth import SetPassword, LoginUser, get_user_token
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token 

urlpatterns = [
    # Auth Routes
    path('', views.index, name ='index'),
    path('api/v.1/auth/setpassword/<str:pk>', SetPassword.as_view(), name = 'setpassword'),
    path('api/v.1/auth/login', LoginUser.as_view(), name = 'login'),
    path('apiv.1/auth/token', get_user_token, name='get_auth_token'),

    # Vendor Routes
    path('api/v.1/vendor/signup', VendorSignUp.as_view(), name = 'vendorsignup'),
    path('api/v.1/vendor/menu', Menu.as_view(), name = 'menu'),
    path('api/v.1/vendor/menu/<int:pk>', MenuDetail.as_view(), name = 'menudetail'),
    path('api/v.1/vendor/order/<int:pk>', VendorOrderDetail.as_view(), name = 'vendororderdetail'),
    path('api/v.1/vendor/orders/status/<int:pk>', OrdersStatus.as_view(), name = 'ordersstatus'),
    path('api/v.1/history/customer/<int:pk>', OrderHistory.as_view(), name = 'orderhistory'),
    path('api/v.1/vendor/sales', VendorSales.as_view(), name = 'vendororderdetail'),
    path('api/v.1/vendor/send/balances', VendorSendBalances.as_view(), name = 'vendororderdetail'),

    # Customer Routes
    path('api/v.1/customer/signup', SignUp.as_view(), name = 'customersignup'),
    path('api/v.1/orderstatus', OrderStatus.as_view(), name = 'orderstatus'),
    path('api/v.1/messagestatus', MessageStatus.as_view(), name = 'orderstatus'),
    path('api/v.1/customer/allmenu', AllMenu.as_view(), name = 'order'),
    path('api/v.1/customer/allmenu/vendor/<int:pk>', VendorAllMenu.as_view(), name = 'vendormenu'),
    path('api/v.1/customer/order', Order.as_view(), name = 'order'),
    path('api/v.1/customer/orders/history', OrdersHistory.as_view(), name = 'ordershistory'),
    path('api/v.1/customer/order/<int:pk>', CustomerOrderDetail.as_view(), name = 'orderdetail'),
    path('api/v.1/customer/order/cancel/<int:pk>', CancelOrder.as_view(), name = 'ordercancellation'),
]
