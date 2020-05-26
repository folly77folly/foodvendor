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
    user_type = 2                       #usertype for customers

    def get(self, request, format=None):
        users = Customer.objects.all()
        serializer = CustomerSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, format = None):
        #check if user exists
        user_type = SignUp.user_type
        user_email = request.data['email']
        query_user = Auth.objects.filter(email = user_email,user_type = user_type)
        if query_user:
            message = {"message" : "user with this email already exists"}
            return Response(message, status = status.HTTP_400_BAD_REQUEST)
        serializer = CustomerSerializer(data=request.data)
        
        subject = "Customer Signup Registration"
        reference_id = id_generator()
        if serializer.is_valid():
            serializer.save()
            createuser(request, reference_id, user_type)
            sendmail(request, reference_id, subject)
            message = {"message":"A password reset link has been sent to your email account. Link expires in 10 mins"}
            return Response(message, status =  status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class AllMenu(APIView):

    permission_classes = (IsAuthenticated,) 
    """
    List all menus avalible that are reoccuring on a particular day.
    """
    # for all the menus avaliable on a particular week of the day
    def get(self, request, format=None):
        today = date.today().strftime('%Y-%m-%d')
        weekday = date.today().strftime('%A').lower()
        all_menu = MenuModel.objects.filter(avaliable=True, freq_of_reocurrence__contains = [weekday])
        serializer = MenuSerializer(all_menu, many=True)
        return Response(serializer.data)

class VendorAllMenu(APIView):
    permission_classes = (IsAuthenticated,) 
    """
    List all menus avalible by vendors.
    """
    # for all the menus avaliable by a vendor
    def get(self, request, pk, format=None):
        all_vendor_menu = MenuModel.objects.filter(vendor_id = pk, avaliable=True)
        serializer = MenuSerializer(all_vendor_menu, many=True)
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
        
    def update_balance (self, customer_obj, charge_amt):
        old_balance = customer_obj.amount_outstanding
        new_balance = old_balance + (charge_amt)
        user_data = {"amount_outstanding":new_balance}
        serializer = CustomerSerializer(customer_obj, data=user_data, partial = True)  
        if serializer.is_valid():
            serializer.save()

    def get(self, request, format=None):
        # collecting details for logged in user
        current_user = request.user
        if current_user.user_type != 2:   #check if this route is been accessed by vendor
            message ={'message':"this resource is for customers"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
                
        data = request.data
        #checking if nothing was ordered
        menus = data['items_ordered']
        if menus == []:
            message = {"message":"No order(s) entered"}
            return Response(message, status = status.HTTP_400_BAD_REQUEST)

        #checking for avaliable menu
        for menu in menus:
            avaliable_menu=self.get_available_object(menu)
            if not avaliable_menu.exists():
                message = {"message":f"Menu ID {menu} is not avalaible kindly remove !"}
                return Response(message, status = status.HTTP_400_BAD_REQUEST)         
        
        amount_due = sum([self.get_object(menu).price for menu in menus])
        message = {'message':f"total amount due {amount_due}"}
        return Response(message, status = status.HTTP_200_OK)


    def post(self, request, format=None):
        # collecting details for logged in user
        current_user = request.user
        if current_user.user_type != 2:   #check if this route is been accessed by vendor
            message ={'message':"this resource is for customers"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        customer_obj = customer_details(current_user)

        #collecting all requests for validations
        data = request.data

        #checking if nothing was ordered
        menus = data['items_ordered']
        if menus == []:
            message = {"message":"No order(s) made"}
            return Response(message, status = status.HTTP_400_BAD_REQUEST)

        #checking for avaliable menu
        for menu in menus:
            avaliable_menu=self.get_available_object(menu)
            if not avaliable_menu.exists():
                message = {"message":f"Menu ID {menu} is not avalaible kindly remove !"}
                return Response(message, status = status.HTTP_400_BAD_REQUEST)    
        
        vendor_id = self.get_object(menus[0]).vendor_id

        #calculating the sum of all ordered items
        amount_due = sum([self.get_object(menu).price for menu in menus])
        paid = data['amount_paid']

        #checking that a positive amount is paid
        if paid < 0 :
            message = {"message":f"amount paid cannot be less than zero. your amount due is {amount_due} naira to complete your order"}
            return Response(message, status = status.HTTP_400_BAD_REQUEST)
        
        #calculating balance left unpaid
        balance =  paid - amount_due

        #setting payment status
        if balance == amount_due :
            payment_status = 1              #no payment
        elif balance < 0 :
            payment_status = 2              #part payment
        elif balance == 0 :
            payment_status = 3              #full payment
        elif balance > 0 :
            payment_status = 4              #excess payment
        else:
            payment_status = 0              #None
        
        #input data for serializer
        order_data = {
        "description" : data['description'],
        "items_ordered" : data['items_ordered'],
        "amount_due" : amount_due,
        "amount_paid" : data['amount_paid'],
        "amount_outstanding" : balance,
        "payment_status" : payment_status,
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

            #updating the customer outstanding
            self.update_balance(customer_obj, balance)

            return Response(message, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrdersHistory(APIView):
    permission_classes = (IsAuthenticated,)
    """
    Retrieve, History of all transactions by customer.
    """
    def get(self, request, format=None):

        # collecting details for logged in user
        current_user = request.user
        if current_user.user_type != 2:   #check if this route is been accessed by vendor
            message ={'message':"this resource is for customers"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        customer_obj = customer_details(request.user)
        order = OrderModel.objects.filter(customer = customer_obj.id).order_by('-date_time_created')
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

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

        # collecting details for logged in user
        current_user = request.user
        if current_user.user_type != 2:   #check if this route is been accessed by vendor
            message ={'message':"this resource is for customers"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        menu = self.get_object(pk)
        #checking if the order url belongs to logged in user
        cust_obj  = customer_details(request.user)
        if cust_obj.id != menu.customer_id :
            message = {"message": "The Selected Order does not belong to you"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        serializer = OrderSerializer(menu)
        return Response(serializer.data)

class CancelOrder(APIView):
    cancel_id = 7
    charge_amt = 200
    permission_classes = (IsAuthenticated,) 
    """
    To cancel a placed order.
    """
    def get_object(self, pk):
        try:
            return OrderModel.objects.get(pk=pk)
        except OrderModel.DoesNotExist:
            raise Http404
    
    def update_balance (self, customer_obj, charge_amt):
        old_balance = customer_obj.amount_outstanding
        new_balance = old_balance -  (charge_amt)
        user_data = {"amount_outstanding":new_balance}
        serializer = CustomerSerializer(customer_obj, data=user_data, partial = True)  
        if serializer.is_valid():
            serializer.save()

    def put(self, request, pk, format=None):         
        
        order = self.get_object(pk)

        #checking if the order url belongs to logged in user
        cust_obj  = customer_details(request.user)

        if cust_obj.id != order.customer_id :
            message = {"message": "The Selected Order does not belong to you"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        
        #checking if the order has not been updated by vendor away from pending and cancel
        if order.order_status_id != 1:
            status_name = OrderStatus.objects.get(pk = order.order_status_id)
            message = {"message": f"This Order cannot be cancelled its now {status_name.name}"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        #checking if the order has not been updated by vendor away from pending and cancel
        now  = timezone.now()
        if now > order.cancel_expiry :  
            message = {"message": "This order cancellation time is expired "}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        order_status = {"order_status" : CancelOrder.cancel_id}                          
        cust_list = [order.customer_id]

        serializer = OrderSerializer(order, data=order_status, partial = True)
        
        if serializer.is_valid():
            serializer.save()
            #charge for cancellation
            self.update_balance(cust_obj, CancelOrder.charge_amt)

            notify_message = f"the order with ID {pk} has been cancelled by customer"
            notify =Notification(order.vendor_id,notify_message,1,cust_list)
            notify.push_notification_to_all()
            message = {"message":f"the order with ID {pk} has been successfully cancelled"}
            return Response(message, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




def customer_details(user_email):
    customer_object = Customer.objects.get(email=user_email)
    return customer_object