from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ...serializers import VendorSerializer, AuthSerializer, MenuSerializer, OrderStatusSerializer, OrdersSerializer, MessageStatusSerializer
from ...models import Vendor, Auth, Menu as MenuModel, OrderStatus as OrderStatusModel, Orders as OrderModel, MessageStatus as MessageStatusModel
from django.core.mail import send_mail
from decouple import config
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from ..helpers import id_generator,sendmail
from ..auth import createuser
from rest_framework.permissions import IsAuthenticated


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
            message = {"message":"Account created successfully a password reset link has been sent to your email account"}
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
        print(vendor_obj.id)
        data = request.data
        menu_data = {
        "name" : data['name'],
        "description" : data['description'],
        "price" : data['price'],
        "quantity" : data['quantity'],
        "is_recurring" : data['is_recurring'],
        "freq_of_reocurrence" : data['freq_of_reocurrence'],
        "vendor" : vendor_obj.id
        }
        serializer  = MenuSerializer(data=menu_data)
        if serializer.is_valid():
            serializer.save()
            message ={"message":f"{data['name']} has been added successfully to your menu list"}
            return Response(message, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MenuDetail(APIView):
    permission_classes = (IsAuthenticated,) 
    """
    Retrieve, update or delete a snippet instance.
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
    Retrieve, all sales report.
    """

    def get(self, request, format=None):
        current_user = request.user
        vendor_obj = vendor_details(current_user)
        print(request.data["date_time_created"])
        record_date =  request.data["date_time_created"]
        queryset = OrderModel.objects.filter(date_time_created=record_date)
        serializer = OrdersSerializer(queryset, many=True)
        # serializer = MenuSerializer(menu)
        return Response(serializer.data)



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