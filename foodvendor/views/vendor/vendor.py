from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ...serializers import VendorSerializer, AuthSerializer, MenuSerializer, OrderStatusSerializer
from ...models import Vendor, Auth, Menu as MenuModel, OrderStatus as OrderStatusModel
from django.core.mail import send_mail
from decouple import config
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from ..helpers import id_generator,sendmail
from ..auth import createuser


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
    """
    List all snippets, or create a new snippet.
    """
    def get(self, request, format=None):
        menu = MenuModel.objects.all()
        serializer = MenuSerializer(menu, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer  = MenuSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MenuDetail(APIView):
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
        serializer = MenuSerializer(menu)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        menu = self.get_object(pk)
        serializer = MenuSerializer(menu, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        menu = self.get_object(pk)
        menu.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderStatus(APIView):
    """
    List all snippets, or create a new snippet.
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