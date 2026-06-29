from django.http import HttpRequest
from django.contrib import messages
from .models import Delegacion
from django.shortcuts import redirect
from users.models import User

def validate_delegacion(request:HttpRequest,nombre)->bool:
    errors = False
    if nombre == '':
        messages.error(request,"Debe indicar un nombre a la delegación",extra_tags='error')
        errors = True
    return errors

def validate_auth_delegacion(request:HttpRequest,delegacion:Delegacion):
    logged_user : User = request.user
    if not delegacion:
        messages.error(request,"La delegación no existe",extra_tags='error')
        return redirect('/backoffice/delegaciones')
    if logged_user.cuenta != delegacion.cuenta:
        return redirect('/AuthError')