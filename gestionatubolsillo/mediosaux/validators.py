from django.http import HttpRequest
from django.contrib import messages
from .models import MedioAuxiliar
from users.models import User
from django.shortcuts import redirect


def validate_medio_auxiliar(request:HttpRequest,nombre)->bool:
    errors = False
    if nombre == '':
        messages.error(request,"Debe indicar un nombre al medio auxiliar",extra_tags='error')
        errors = True
    return errors

def validate_medio_auth(request:HttpRequest,medioaux:MedioAuxiliar|None):
    if not medioaux:
        messages.error(request,"El medio auxiliar no existe",extra_tags='error')
        return redirect('/backoffice/medios_auxiliares')
    user : User = request.user
    if user.cuenta != medioaux.cuenta:
        return redirect('/AuthError')