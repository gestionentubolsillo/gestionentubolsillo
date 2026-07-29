from django.contrib import messages
from django.http import HttpRequest
from .models import Empresa
from users.models import User
from django.shortcuts import redirect

def validate_empresa(request:HttpRequest,nombre,paquete)->bool:
    errors = False
    if nombre == '' or paquete == '':
        messages.error(request,"Todos los campos son obligatorios",extra_tags='error')
        errors = True
    if paquete != '':
        paquetes_validos = dict(Empresa._meta.get_field('paquete').choices).keys()
        if paquete not in paquetes_validos:
            messages.error(request, "El paquete seleccionado no es válido", extra_tags='error')
            errors = True
    return errors


def validate_auth_empresa(request:HttpRequest,empresa:Empresa):
    logged_user : User = request.user
    if not empresa:
        messages.error(request,"La empresa no existe",extra_tags='error')
        return redirect('/backoffice/empresas')
    if logged_user.cuenta != empresa.cuenta:
        return redirect('/AuthError')