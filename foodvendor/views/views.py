from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
import webbrowser

# Create your views here.

def index(request):
    # return HttpResponse("<h3>Welcome to VGG internship project<h3>")
    webbrowser.open("https://documenter.getpostman.com/view/8806253/SztBa7TL?version=latest#64f8e2f7-353e-4931-9594-442970a1b59f][docs")
