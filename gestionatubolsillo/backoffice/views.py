from django.shortcuts import render, redirect
from django.http import HttpRequest
from users.models import User

# Create your views here.

def show_backoffice(request:HttpRequest):
    user : User = request.user
    if not user.is_authenticated:
        return redirect('/login')
    context = {
        'user':user
    }
    return render(request,'backoffice/home.html',context)