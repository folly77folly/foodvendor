from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ...serializers import VendorSerializer, AuthSerializer, MenuSerializer, OrderStatusSerializer, OrdersSerializer, MessageStatusSerializer, NotificationSerializer
from ...models import Vendor, Auth, Menu as MenuModel, OrderStatus as OrderStatusModel, Orders as OrderModel, MessageStatus as MessageStatusModel
from ...models import Customer
from django.core.mail import send_mail
from decouple import config
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from ..helpers import id_generator,sendmail, Notification
from ..auth import createuser
from rest_framework.permissions import IsAuthenticated
import datetime
from django.utils.timezone import make_aware


class VendorSignUp(APIView):

    def post(self, request, format = None):
        user_type = 1
        subject = "Vendor Signup Registration"
        serializer = VendorSerializer(data=request.data)
        reference_id = id_generator()
        if serializer.is_valid():
            serializer.save()
            createuser(request, reference_id, user_type)
            sendmail(request, reference_id, subject)
            message = {"message":"Account created successfully a password reset link has been sent to your email account. Link expires in 10 mins"}
            return Response(message, status =  status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)



class Menu(APIView):
    permission_classes = (IsAuthenticated,) 
    """
    List all menu, or create a new menu.
    """
    def get_object(self, vid):

        try:
            return MenuModel.objects.get(vendor=vid)
        except MenuModel.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        current_user = request.user
        vendor_obj = vendor_details(current_user)
        print(vendor_obj.id)
        queryset = MenuModel.objects.filter(vendor=vendor_obj.id)
        serializer = MenuSerializer(queryset, many=True)
        # serializer = MenuSerializer(menu)
        return Response(serializer.data)

    def post(self, request, format=None):
        current_user = request.user
        vendor_obj = vendor_details(current_user)
        business_name = vendor_obj.business_name
        cust_list =  list(Customer.objects.all().values_list('id',flat=True))
        data = request.data

        #checking if order is recurring or not
        print(data['is_recurring'])
        if data['is_recurring'] == "True":
            menu_data = {
            "name" : data['name'],
            "description" : data['description'],
            "price" : data['price'],
            "quantity" : data['quantity'],
            "is_recurring" : data['is_recurring'],
            "freq_of_reocurrence" : data['freq_of_reocurrence'],
            "vendor" : vendor_obj.id
            }
        else:
            menu_data = {
            "name" : data['name'],
            "description" : data['description'],
            "price" : data['price'],
            "quantity" : data['quantity'],
            "is_recurring" : data['is_recurring'],
            "vendor" : vendor_obj.id
            }
        print(menu_data)         
        serializer  = MenuSerializer(data=menu_data)
        if serializer.is_valid():
            serializer.save()
            notify_message = f"A New menu {data['name']} has been added by {business_name} "
            notify = Notification(vendor_obj.id,notify_message,2,cust_list)
            notify.push_notification_to_all()
            message ={"message":f"{data['name']} has been added successfully to your menu list"}
            return Response(message, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MenuDetail(APIView):
    permission_classes = (IsAuthenticated,) 
    """
    Retrieve, update or delete a menu instance.
    """
    def get_object(self, pk):
        try:
            return MenuModel.objects.get(pk=pk)
        except MenuModel.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        menu = self.get_object(pk)
        current_user = request.user
        vendor_obj = vendor_details(current_user)
        print(menu.vendor_id)
        if menu.vendor_id != vendor_obj.id:
            message = {"message":"This Menu does not belong to you, Preview is not Allowed"}
            return Response(message, status = status.HTTP_400_BAD_REQUEST)        
        serializer = MenuSerializer(menu)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        menu = self.get_object(pk)
        current_user = request.user
        vendor_obj = vendor_details(current_user)
        print(menu.vendor_id)
        if menu.vendor_id != vendor_obj.id:
            message = {"message":"This Menu does not belong to you, Update is not Allowed"}
            return Response(message, status = status.HTTP_400_BAD_REQUEST)
        serializer = MenuSerializer(menu, data=request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        menu = self.get_object(pk)
        current_user = request.user
        vendor_obj = vendor_details(current_user)
        print(menu.vendor_id)
        if menu.vendor_id != vendor_obj.id:
            message = {"message":"This Menu does not belong to you, Delete is not Allowed"}
            return Response(message, status = status.HTTP_400_BAD_REQUEST)
        menu.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class VendorOrderDetail(APIView):
    permission_classes = (IsAuthenticated,) 
    """
    Retrieve, update or delete a snippet instance.
    """
    def get_object(self, pk):
        try:
            return OrderModel.objects.get(pk=pk)
        except OrderModel.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        order = self.get_object(pk)
        current_user = request.user
        vendor_obj = vendor_details(current_user)
        print(order.vendor_id)
        if order.vendor_id != vendor_obj.id:
            message = {"message":"This Order does not belong to you, Preview is not Allowed"}
            return Response(message, status = status.HTTP_400_BAD_REQUEST)        
        serializer = OrdersSerializer(order)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        order = self.get_object(pk)
        current_user = request.user
        vendor_obj = vendor_details(current_user)
        print(request.data)
        if len(request.data) != 1 or 'order_status' not in request.data:
            message = {"message":"you are only allowed to update order status from customer order"}
            return Response(message, status = status.HTTP_400_BAD_REQUEST)
        
        order_status = {"order_status" : request.data["order_status"]}
        print(order_status)
        if order.vendor_id != vendor_obj.id:
            message = {"message":"This Order does not belong to you, Update is not Allowed"}
            return Response(message, status = status.HTTP_400_BAD_REQUEST)
        serializer = OrdersSerializer(order, data=order_status, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VendorSales(APIView):
    permission_classes = (IsAuthenticated,) 
    """
    Retrieve, all sales report for a date.
    """
    def get(self, request, format=None):
        if 'date_time_created' not in request.data:
            message ={"message":"this request requires date_time_created e.g 2020-05-25"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        current_user = request.user
        vendor_obj = vendor_details(current_user)
        search_date = request.data["date_time_created"]
        queryset = OrderModel.objects.filter(date_time_created__date = search_date, vendor_id = vendor_obj.id)
        serializer = OrdersSerializer(queryset, many=True)
        return Response(serializer.data)

class VendorSendBalances(APIView):
    permission_classes = (IsAuthenticated,) 
    """
    Send and generate all balances for Customers.
    """
    #report for all balances owed or over credited
    def get(self, request, format=None):
        current_user = request.user
        vendor_obj = vendor_details(current_user)
        qry_orders = OrderModel.objects.filter(vendor_id = vendor_obj.id).exclude(amount_outstanding = 0.00)
        serializer = OrdersSerializer(qry_orders, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)            

    #sending all balances owed or over credited to customers by notification
    def post(self, request, format=None):
        current_user = request.user
        vendor_obj = vendor_details(current_user)
        orders = OrderModel.objects.filter(vendor_id = vendor_obj.id).exclude(amount_outstanding = 0.00)
        if orders :
            for order in orders:
                notify_message = f"This is to notify you your balace with us is {order.amount_outstanding} "
                notify = Notification(vendor_obj.id,notify_message,2,[order.customer_id])
                notify.push_notification_to_all()

            message ={"message":"All balances sent successfully"}
            return Response(message, status = status.HTTP_200_OK )
        message ={"message":"No balances to be sent"}
        return Response(message, status = status.HTTP_200_OK )

class OrderHistory(APIView):
    permission_classes = (IsAuthenticated,) 
    """
    gets all orders history for a Customer from my store.
    """

    def get(self, request, pk, format=None):
        current_user = request.user
        vendor_obj = vendor_details(current_user)
        qry_orders_by_user = OrderModel.objects.filter(vendor_id = vendor_obj.id,customer_id = pk)
        serializer = OrdersSerializer(qry_orders_by_user, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK) 

class OrdersStatus(APIView):
    permission_classes = (IsAuthenticated,) 
    """
    gets reports for all orders pending,in-progress,pending and cancelled orders for a date.
    """

    def get(self, request, pk, format=None):
        current_user = request.user
        vendor_obj = vendor_details(current_user)

        if 'order_date' in request.data :
            order_date = request.data['order_date']
            qry_orders_by_user = OrderModel.objects.filter(vendor_id = vendor_obj.id,order_status_id = pk, delivery_date_time__date = order_date)
            serializer = OrdersSerializer(qry_orders_by_user, many=True)
            return Response(serializer.data, status = status.HTTP_200_OK)
        message ={"message":"order_date field is missing"}
        return Response(message, status = status.HTTP_400_BAD_REQUEST)

class OrderStatus(APIView):
    """
    List all order status, or create a new order status.
    """
    def get(self, request, format=None):
        order_status = OrderStatusModel.objects.all()
        serializer = OrderStatusSerializer(order_status, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer  = OrderStatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MessageStatus(APIView):
    """
    List all order status, or create a new order status.
    """
    def get(self, request, format=None):
        message_status = MessageStatusModel.objects.all()
        serializer = MessageStatusSerializer(message_status, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer  = MessageStatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def vendor_details(user_email):
    Vendor_object = Vendor.objects.get(email=user_email)
    return Vendor_object