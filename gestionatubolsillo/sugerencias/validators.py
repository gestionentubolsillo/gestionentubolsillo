from django.contrib import messages
from django.http import HttpRequest
from users.models import User
from .models import Sugerencia
from django.shortcuts import redirect




def validate_sugerencia(request:HttpRequest, texto, usuario_referente_id)->bool:
    errors = False
    try:
        user_ref = User.objects.filter(UserID=usuario_referente_id,cuenta=request.user.cuenta).first()
    except ValueError:
        user_ref = None
    if texto == '':
        messages.error(request, 'El texto de la sugerencia no puede estar vacío.',extra_tags='error')
        errors = True
    if not user_ref:
        messages.error(request, 'El usuario referente no es válido.',extra_tags='error')
        errors = True
    return errors

def validate_auth_sugerencia(request:HttpRequest,sugerencia:Sugerencia):
    logged_user : User = request.user
    if not sugerencia:
        messages.error(request,"La Sugerencia no existe", extra_tags='error')
        return redirect('/backoffice/sugerencias')
    if logged_user.cuenta != sugerencia.cuenta:
        return redirect('/AuthError')
    return None