from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
import datetime
from django.utils import timezone

from .managers import CustomUserManager

# Create your models here.
class Auth(AbstractBaseUser):
    email = models.EmailField( max_length=60, unique = True)
    password = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    reference_id = models.CharField(max_length = 30)
    user_type = models.IntegerField(default = 1)
    date_expiry = models.DateTimeField(default = timezone.now()+ timezone.timedelta(minutes = 10), blank=True)
    date_time_created = models.DateTimeField(auto_now_add=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password',]
    
    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Vendor(models.Model):
    email = models.EmailField(max_length=60,  unique = True)
    business_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=11)
    date_time_created = models.DateTimeField( auto_now_add=True)

    def __str__(self):
        return self.email

class Customer(models.Model):
    first_name = models.CharField( max_length=255)
    last_name = models.CharField( max_length=255)
    email = models.EmailField(max_length=60,  unique = True)
    phone_number = models.CharField(max_length=11)
    date_time_created = models.DateTimeField(auto_now_add=True)
    amount_outstanding = models.FloatField(default = 0.00)

    def __str__(self):
        return self.email    

class Menu(models.Model):
    BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))

    vendor = models.ForeignKey(Vendor, on_delete = models.CASCADE)
    name = models.CharField( max_length=255)
    description = models.CharField( max_length=255)
    price = models.FloatField(default = 0.00)
    quantity = models.IntegerField()
    is_recurring = models.BooleanField(choices = BOOL_CHOICES)
    avaliable = models.BooleanField(choices = BOOL_CHOICES, default= True)
    freq_of_reocurrence = ArrayField(models.CharField(max_length=10, blank=True),size=8,default=list)
    date_time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class OrderStatus(models.Model):
    name = models.CharField(max_length=50)

class Orders(models.Model):
    BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))

    customer = models.ForeignKey(Customer, on_delete = models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete = models.CASCADE)
    description = models.CharField(max_length=255)
    items_ordered = ArrayField(models.IntegerField(),default=list)
    amount_due = models.FloatField(default = 0.00)
    amount_paid = models.FloatField(default = 0.00)
    amount_outstanding = models.FloatField(default = 0.00)
    paid = models.BooleanField(choices = BOOL_CHOICES, default = False)
    order_status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE, default=1)
    cancel_expiry = models.DateTimeField(default = timezone.now()+ datetime.timedelta(minutes = 10), blank=True)
    delivery_date_time = models.DateTimeField(default = timezone.now(), blank=True)
    date_time_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.description

class MessageStatus(models.Model):
    name = models.CharField(max_length=50)

class Notification(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete = models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE)
    message_status = models.ForeignKey(MessageStatus, on_delete = models.CASCADE)
    message = models.CharField(max_length = 255)
    date_time_created = models.DateTimeField(auto_now_add=True)


