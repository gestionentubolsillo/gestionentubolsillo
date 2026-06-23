from django.http import HttpRequest
from django.contrib import messages


def validate_central(request:HttpRequest,nombre)->bool:
    errors = False
    if nombre == '':
        messages.error(request,"Debe indicar un nombre a la central receptora",extra_tags='error')
        errors = True
    return errors
