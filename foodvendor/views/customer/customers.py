from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ...serializers import CustomerSerializer, AuthSerializer
from ...models import Customer,Auth
from django.core.mail import send_mail
from decouple import config
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

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
        data = request.data
        print(data)
        email = data['email']
        password ="pass"
        userdata = {'email': email,'password':password}
        print(userdata)
        authseuserdatarializer = AuthSerializer(data=userdata)
        print(data['email'])
        if serializer.is_valid():
            serializer.save()
            authseuserdatarializer.is_valid()
            authseuserdatarializer.save()
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


class VendorMenu(APIView):
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