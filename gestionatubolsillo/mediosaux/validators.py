from django.http import HttpRequest
from django.contrib import messages
from .models import MedioAuxiliar
from users.models import User
from django.shortcuts import redirect

from auditloggers.handlers import save_log

def validate_medio_auxiliar(request:HttpRequest,nombre)->bool:
    errors = False
    if nombre == '':
        messages.error(request,"Debe indicar un nombre al medio auxiliar",extra_tags='error')
        errors = True
    return errors

def validate_medio_auth(request:HttpRequest,medioaux:MedioAuxiliar|None):
    if not medioaux:
        save_log(request, apartado='MEDIO_AUX', accion='ERROR', id_user=request.user.pk, id_cuenta=request.user.cuenta.pk,info='Intento de acceder a un medio auxiliar que no existe')
        messages.error(request,"El medio auxiliar no existe",extra_tags='error')
        return redirect('/backoffice/medios_auxiliares')
    user : User = request.user
    if user.cuenta != medioaux.cuenta:
        save_log(request, apartado='MEDIO_AUX', accion='UNAUTH', id_user=request.user.pk, id_cuenta=medioaux.cuenta.pk,info=f'Intento de acceder a medio auxiliar con ID: {medioaux.MedioAuxiliarID} sin autorización')
        return redirect('/AuthError')