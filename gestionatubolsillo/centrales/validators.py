from django.http import HttpRequest, HttpResponseForbidden
from django.contrib import messages
from .models import Central
from users.models import User
from django.shortcuts import redirect

from auditloggers.handlers import save_log

def validate_central(request:HttpRequest,nombre)->bool:
    errors = False
    if nombre == '':
        messages.error(request,"Debe indicar un nombre a la central receptora",extra_tags='error')
        errors = True
    return errors

def validate_auth_central(request:HttpRequest,central:Central):
    logged_user : User = request.user
    if not central:
        save_log(request, apartado='CENTRAL', accion='ERROR', id_user=request.user.pk, id_cuenta=request.user.cuenta.pk,info='La central receptora no existe')
        messages.error(request,"La central receptora no existe",extra_tags='error')
        return redirect('/backoffice/centrales')
    if logged_user.cuenta != central.cuenta:
        save_log(request, apartado='CENTRAL', accion='UNAUTH', id_user=request.user.pk, id_cuenta=central.cuenta.pk,info='El usuario no tiene acceso a la central receptora')
        return redirect('/AuthError')