from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ...serializers import CustomerSerializer, AuthSerializer, OrderSerializer
from ...models import Customer,Auth, Orders as OrderModel, Menu as MenuModel
from django.core.mail import send_mail
from decouple import config
from django.utils import timezone
from ..helpers import id_generator,sendmail
from ..auth import createuser
from rest_framework.permissions import IsAuthenticated


class SignUp(APIView):
    """
    List all users, or create a new user.
    """
    def get(self, request, format=None):
        users = Customer.objects.all()
        serializer = CustomerSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, format = None):
        serializer = CustomerSerializer(data=request.data)
        user_type = 2
        subject = "Customer Signup Registration"
        reference_id = id_generator()
        if serializer.is_valid():
            serializer.save()
            createuser(request, reference_id, user_type)
            sendmail(request, reference_id, subject)
            message = {"message":"A password reset link has been sent to your email account"}
            return Response(message, status =  status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class Order(APIView):
    permission_classes = (IsAuthenticated,) 
    """
    List all orders, or create a new order.
    """
    def get_object(self, pk):
        try:
            return MenuModel.objects.get(pk=pk)
        except MenuModel.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        # order = OrderModel.objects.all()
        customer_obj = customer_details(request.user)
        order = OrderModel.objects.filter(customer = customer_obj.id)
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        current_user = request.user
        customer_obj = customer_details(current_user)
        print(customer_obj.id)
        data = request.data
        menus = data['items_ordered']
        if menus == []:
            message = {"message":"No order(s) made"}
            return Response(message, status = status.HTTP_400_BAD_REQUEST)
        vendor_id = self.get_object(menus[0]).vendor_id
        amount_due = sum([self.get_object(menu).price for menu in menus])
        print(amount_due)
        if data['amount_paid'] != amount_due :
            message = {"message":f"amount paid must be equal to amount due. Ensure to pay {amount_due} naira to complete your order"}
            return Response(message, status = status.HTTP_400_BAD_REQUEST)
        order_data = {
        "description" : data['description'],
        "items_ordered" : data['items_ordered'],
        "amount_due" : amount_due,
        "amount_paid" : data['amount_paid'],
        "amount_outstanding" : 0,
        "paid" : True,
        "vendor" : vendor_id,
        "customer" : customer_obj.id,
        "delivery_date_time" : data['delivery_date_time'],
        "order_status_id" : 1
        }        
        serializer  = OrderSerializer(data=order_data)
        if serializer.is_valid():
            serializer.save()
            message = {"message":"Your Order has been Placed successfully"}
            # send_notification
            return Response(message, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerOrderDetail(APIView):
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
        menu = self.get_object(pk)
        serializer = OrderSerializer(menu)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        menu = self.get_object(pk)
        serializer = OrderSerializer(menu, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        menu = self.get_object(pk)
        menu.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def customer_details(user_email):
    Customer_object = Customer.objects.get(email=user_email)
    return Customer_object