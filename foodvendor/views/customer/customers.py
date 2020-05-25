from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ...serializers import CustomerSerializer, AuthSerializer, OrderSerializer, MenuSerializer
from ...models import Customer,Auth, Orders as OrderModel, Menu as MenuModel, OrderStatus
from django.core.mail import send_mail
from decouple import config
from django.utils import timezone
from ..helpers import id_generator,sendmail, Notification
from ..auth import createuser
from rest_framework.permissions import IsAuthenticated
from datetime import date


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

class AllMenu(APIView):

    permission_classes = (IsAuthenticated,) 
    """
    List all menus avalible that are reoccuring on a particular day.
    """
    def get(self, request, format=None):
        today = date.today().strftime('%Y-%m-%d')
        weekday = date.today().strftime('%A').lower()
        all_menu = MenuModel.objects.filter(avaliable=True, freq_of_reocurrence__contains = ['tuesday'])
        serializer = MenuSerializer(all_menu, many=True)
        return Response(serializer.data)

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
    
    def get_available_object(self, pk):
        menu_record = MenuModel.objects.filter(pk = pk ,avaliable=True)
        return menu_record
        

    def get(self, request, format=None):
        # order = OrderModel.objects.all()
        customer_obj = customer_details(request.user)
        order = OrderModel.objects.filter(customer = customer_obj.id)
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        # collecting details for logged in user
        current_user = request.user
        customer_obj = customer_details(current_user)
        print(customer_obj.id)

        #collecting all requests for validations
        data = request.data

        #checking if nothing was ordered
        menus = data['items_ordered']
        if menus == []:
            message = {"message":"No order(s) made"}
            return Response(message, status = status.HTTP_400_BAD_REQUEST)

        #checkin for avaliable menu
        for menu in menus:
            avaliable_menu=self.get_available_object(menu)
            if not avaliable_menu.exists():
                message = {"message":f"Menu ID {menu} is not avalaible kindly remove !"}
                return Response(message, status = status.HTTP_400_BAD_REQUEST)    
        
        vendor_id = self.get_object(menus[0]).vendor_id

        #calculating the sum of all ordered items
        amount_due = sum([self.get_object(menu).price for menu in menus])
        print(amount_due)
        paid = data['amount_paid']

        #checking that a positive amount is paid
        if paid < 0 :
            message = {"message":f"amount paid cannot be less than zero. your amount due is {amount_due} naira to complete your order"}
            return Response(message, status = status.HTTP_400_BAD_REQUEST)
        
        #calculating balance left unpaid
        balance =  paid - amount_due
        
        #input data for serializer
        order_data = {
        "description" : data['description'],
        "items_ordered" : data['items_ordered'],
        "amount_due" : amount_due,
        "amount_paid" : data['amount_paid'],
        "amount_outstanding" : balance,
        "paid" : True,
        "vendor" : vendor_id,
        "customer" : customer_obj.id,
        "delivery_date_time" : data['delivery_date_time'],
        "order_status_id" : 1 #pending
        }

        #saving record for a new order
        serializer  = OrderSerializer(data=order_data)
        if serializer.is_valid():
            serializer.save()
            message = {"message":"Your Order has been Placed successfully"}

            # send_notification to vendor
            cust_list = [customer_obj.id]
            order = OrderModel.objects.latest('id')
            notify_message = f"A new order with id {order.id} has been placed for {data['description']}"
            notify = Notification(vendor_id,notify_message,1,cust_list)
            notify.push_notification_to_all()

            return Response(message, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerOrderDetail(APIView):
    permission_classes = (IsAuthenticated,) 
    """
    Retrieve, update or cancel a placed order.
    """
    def get_object(self, pk):
        try:
            return OrderModel.objects.get(pk=pk)
        except OrderModel.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        menu = self.get_object(pk)
        #checking if the order url belongs to logged in user
        cust_obj  = customer_details(request.user)
        print(cust_obj.id)
        print(menu.customer_id)
        if cust_obj.id != menu.customer_id :
            message = {"message": "The Selected Order does not belong to you"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        serializer = OrderSerializer(menu)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        menu = self.get_object(pk)

        #checking if the order url belongs to logged in user
        cust_obj  = customer_details(request.user)
        print(cust_obj.id)
        print(menu.customer_id)
        if cust_obj.id != menu.customer_id :
            message = {"message": "The Selected Order does not belong to you"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        
        #checking if the order has not been updated by vendor away from pending and cancel
        print(menu.order_status_id)
        if menu.order_status_id != 1:
            # result = OrderModel.objects.filter(orderstatus__id = 1)
            # result2 = OrderStatus.objects.filter(orders = menu.order_status_id)
            # print(result)
            message = {"message": "This Order cannot be cancelled"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)            
        cust_list = [menu.customer_id]
        serializer = OrderSerializer(menu, data=request.data, partial = True)
        
        if serializer.is_valid():
            serializer.save()
            notify_message =f"the order with ID {menu.id} has been updated "
            notify =Notification(menu.vendor_id,notify_message,1,cust_list)
            notify.push_notification_to_all()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, pk, format=None):
    #     menu = self.get_object(pk)
    #     menu.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


def customer_details(user_email):
    customer_object = Customer.objects.get(email=user_email)
    return customer_object