from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ...serializers import CustomerSerializer, AuthSerializer, OrderSerializer
from ...models import Customer,Auth, Orders as OrderModel
from django.core.mail import send_mail
from decouple import config
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone
from ..helpers import id_generator,sendmail
from ..auth import createuser


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


# class SetPassword(APIView):
#     """
#     List all users, or create a new user.
#     """
#     def get_object(self, pk):
#         try:
#             return Auth.objects.get(reference_id=pk)
#         except Auth.DoesNotExist:
#             raise Http404
        
#     def get(self, request, format=None):
#         users = Auth.objects.all()
#         serializer = AuthSerializer(users, many=True)
#         return Response(serializer.data)

#     def post(self, request, format = None):
#         serializer = AuthSerializer(data=request.data)
#         data = request.data
#         # token = Token.objects.create(user = data)
#         print(data)
#         # print(token)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status =  status.HTTP_201_CREATED)
#         return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

#     def put(self, request, pk, format=None):
#         user = self.get_object(pk)
#         now = timezone.now()
#         if now < user.date_expiry :
#             user_obj = Auth.objects.get(email = user)
#             new_password = request.data['password']
#             user_obj.set_password(new_password)
#             user_obj.save()
#             return Response( status =  status.HTTP_201_CREATED)
#         message ={"message":"The password reset link has exipred"}
#         return Response(message,status = status.HTTP_400_BAD_REQUEST)


# class LoginUser(APIView):
#     """
#     List all users, or create a new user.
#     """
#     def post(self, request, format = None):
#         data = request.data
#         email = data['email']
#         password = data['password']
#         user = authenticate(email = email, password = password)
#         if user is None :
#             response = {"message" : "Incorrect username or password details"}
#             return Response(response, status = status.HTTP_400_BAD_REQUEST)
#         response = {"message" : "You are logged in welcome back"}
#         return Response(response, status =  status.HTTP_200_OK)


class Order(APIView):
    """
    List all snippets, or create a new snippet.
    """
    def get(self, request, format=None):
        order = OrderModel.objects.all()
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer  = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderDetail(APIView):
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