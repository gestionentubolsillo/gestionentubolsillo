from django.http import HttpRequest
from django.contrib import messages
from .models import Delegacion
from django.shortcuts import redirect
from users.models import User

from auditloggers.handlers import save_log

def validate_delegacion(request:HttpRequest,nombre)->bool:
    errors = False
    if nombre == '':
        messages.error(request,"Debe indicar un nombre a la delegación",extra_tags='error')
        errors = True
    return errors

def validate_auth_delegacion(request:HttpRequest,delegacion:Delegacion):
    logged_user : User = request.user
    if not delegacion:
        save_log(request, apartado='DELEGACION', accion='ERROR', id_user=request.user.pk, id_cuenta=request.user.cuenta.pk,info='Intento de acceder a una delegación que no existe')
        messages.error(request,"La delegación no existe",extra_tags='error')
        return redirect('/backoffice/delegaciones')
    if logged_user.cuenta != delegacion.cuenta:
        save_log(request, apartado='DELEGACION', accion='UNAUTH', id_user=request.user.pk, id_cuenta=delegacion.cuenta.pk,info=f'Intento de acceder a delegación con ID: {delegacion.DelegacionID} sin autorización')
        return redirect('/AuthError')