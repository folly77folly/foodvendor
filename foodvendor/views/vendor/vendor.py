from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ...serializers import VendorSerializer, AuthSerializer, MenuSerializer
from ...models import Vendor, Auth, Menu as MenuModel
from django.core.mail import send_mail
from decouple import config
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist


class SignUp(APIView):
    def post(self, request, format = None):

        serializer = VendorSerializer(data=request.data)
        data = request.data
        print(data['email'])
        if serializer.is_valid():
            serializer.save()
            to = [data['email']]
            base_url =  config("BASE_URL")
            set_password_url = config("SET_PASSWORD_URL", default="http://localhost:3000/reset-password")
            subject = "Vendor Signup Registration"
            link_message = f'<a href="{base_url+set_password_url}">Set password</a>'
            message = "A set password link has been sent to your Email account"
            SENDER = config("EMAIL_HOST_USER", default="ppmogunstatealerts@gmail.com")
            from_email = SENDER
            html_content = f"Click on the link below to set your password\n{link_message}"
            send_mail(subject, message , from_email, to, fail_silently=False,)
            return Response(serializer.data, status =  status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def sendmail(self, request):
        print('here')
        send_mail(
            'Subject here',
            'Here is the message.',
            'from@example.com',
            ['iamaqim@gmail.com'],
            fail_silently=False,
        )

class SetPassword(APIView):
    """
    List all users, or create a new user.
    """
    def get(self, request, format=None):
        users = Auth.objects.all()
        serializer = AuthSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, format = None):
        serializer = AuthSerializer(data=request.data)
        data = request.data
        # token = Token.objects.create(user = data)
        print(data)
        # print(token)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status =  status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)        

class LoginUser(APIView):
    """
    List all users, or create a new user.
    """
    def post(self, request, format = None):
        data = request.data
        email = data['email']
        password = data['password']
        user = authenticate(email = email, password = password)
        if user is None :
            response = {"message" : "Incorrect username or password details"}
            return Response(response, status = status.HTTP_400_BAD_REQUEST)
        response = {"message" : "You are logged in welcome back"}
        return Response(response, status =  status.HTTP_200_OK)


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