from django.contrib import messages
from django.http import HttpRequest

def validate_empresa(request:HttpRequest,nombre,paquete)->bool:
    errors = False
    if nombre == '' or paquete == '':
        messages.error(request,"Todos los campos son obligatorios",extra_tags='error')
        errors = True
    return errors