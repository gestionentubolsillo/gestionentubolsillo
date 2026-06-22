from django.contrib import messages
from django.http import HttpRequest
from users.models import User




def validate_sugerencia(request:HttpRequest, texto, usuario_referente_id)->bool:
    errors = False
    user_ref = User.objects.filter(UserID=usuario_referente_id).first()
    if texto == '':
        messages.error(request, 'El texto de la sugerencia no puede estar vacío.',extra_tags='error')
        errors = True
    if not user_ref:
        messages.error(request, 'El usuario referente no es válido.',extra_tags='error')
        errors = True
    return errors