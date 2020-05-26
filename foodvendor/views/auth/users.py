from django.http import Http404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ...serializers import CustomerSerializer, AuthSerializer, OrderSerializer
from ...models import Customer, Auth, Orders as OrderModel
from ..helpers import id_generator
from decouple import config
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone


class SetPassword(APIView):
    """
    list a user ,Set your password
    """
    def get_object(self, pk):
        try:
            return Auth.objects.get(reference_id = pk)
        except Auth.DoesNotExist:
            raise Http404
        
    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        message = {"message":f"{user},use a PUT request to set your password"}
        return Response(message, status = status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        user = self.get_object(pk)
        now = timezone.now()
        if now < user.date_expiry :
            user_obj = Auth.objects.get(email = user)
            new_password = request.data['password']
            user_obj.set_password(new_password)
            user_obj.save()
            message ={"message":"Your password has now been set you can now login"}
            return Response(message, status =  status.HTTP_200_OK)
        message ={"message":"The password reset link has exipred"}
        return Response(message,status = status.HTTP_400_BAD_REQUEST)


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
        user_token = get_token(request)
        response = {
            "message" : "You are logged in welcome back",
            "token" : user_token
            }
        update_last_login(email)
        return Response(response, status =  status.HTTP_200_OK)

def createuser(request, reference_id, user_type):
    data = request.data
    email = data['email']
    default_password = config("DEFAULT_PASSWORD")
    userdata = {'email': email,'password':default_password, 'reference_id':reference_id, 'user_type' : user_type }
    authseuserdatarializer = AuthSerializer(data=userdata)
    if authseuserdatarializer.is_valid():
        authseuserdatarializer.save()

@api_view(['POST'])
def get_user_token(request):
    user_obj = Auth.objects.get(email = request.data['email'])
    if request.method == 'POST':
        token = Token.objects.filter(user=user_obj)
        if token:
            new_key = token[0].generate_key()
            token.update(key=new_key)
            return Response({"token":new_key})
        else:
            token = Token.objects.create(user = user_obj)
            return Response({"token":token.key})

def get_token(request):
    user_obj = Auth.objects.get(email = request.data['email'])
    if request.method == 'POST':
        token = Token.objects.filter(user=user_obj)
        if token:
            new_key = token[0].generate_key()
            token.update(key=new_key)
            return new_key
        else:
            token = Token.objects.create(user = user_obj)
            return token.key

def update_last_login(email):
    user_obj = Auth.objects.get(email = email)
    update_data ={"last_login":timezone.now()}
    serializer = AuthSerializer(user_obj, data = update_data, partial = True)
    if serializer.is_valid():
        serializer.save()
